import os
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Generator, NamedTuple

import requests

from helpers.db import get_cursor

CONFIG = {"HKT": ["192.168.31.1"], "MOW": ["192.168.32.1"], "SPB": ["192.168.33.3"]}


@dataclass
class Login:
    user_id: str
    username: str
    ip: str
    office: Optional[str]
    last_date: datetime
    email: str = None
    tz: str = None

    def to_dict(self) -> Dict:
        return self.__dict__


class UserExtraInfo(NamedTuple):
    email: str
    tz: Optional[str]


class SlackLogger:
    SLACK_TOKEN = os.getenv("SLACK_BOT_TOKEN")
    SLACK_USERS_LIST_URL = "https://slack.com/api/users.list"
    SAVE_QUERY = """
        INSERT INTO 
            slack_logins(user_id, username, ip, office, last_date, email, user_tz, pdate) 
        VALUES (%(user_id)s, %(username)s, %(ip)s, %(office)s, %(last_date)s, %(email)s, %(tz)s, NOW()::date)
        ON CONFLICT (user_id, pdate) DO UPDATE SET 
        ip = EXCLUDED.ip, office = excluded.office, last_date = excluded.last_date, user_tz = excluded.user_tz;
        """

    def __init__(self):
        self.api_url = os.getenv("SLACK_API_URL")
        self.config = self.get_config()
        self.result_map = {}
        self.params = {}

    def get_config(self) -> Dict:
        """ For future realisation"""
        return CONFIG

    def run(self):
        results: Dict[str, List[Login]] = defaultdict(list)
        for data in self.get_slack_logs():
            for k, v in data.items():
                results[k].append(v)

        filtered = self.filter_results(results)
        mapper = self.get_user_extra_info()
        for k, v in mapper.items():
            if filtered.get(k):
                filtered[k].email = v.email
                filtered[k].tz = v.tz

        self.save_to_db(filtered)

    def detect_office(self, ip: str) -> Optional[str]:
        for k, v in self.config.items():
            if ip in v:
                return k
        return None

    def get_slack_logs(self) -> Generator[Dict[str, Login], None, None]:
        while True:
            result: Dict[str, List[Login]] = defaultdict(list)
            response = requests.get(self.api_url, params=self.params)
            response.raise_for_status()
            data = response.json()

            if not data["ok"]:
                return

            # Set params for next request
            paging = data["paging"]
            self.params = {"page": paging["page"] + 1}

            for item in data["logins"]:
                if item["user_agent"].startswith("ApiApp"):
                    continue

                last_date = datetime.fromtimestamp(item["date_last"])
                if last_date.date() < datetime.today().date():
                    return

                login = Login(
                    user_id=item.get("user_id"),
                    username=item.get("username"),
                    ip=item.get("ip"),
                    office=self.detect_office(item.get("ip")),
                    last_date=last_date,
                )
                result[item.get("user_id")].append(login)

            yield self.filter_results(result)

    @staticmethod
    def filter_results(result: Dict[str, List[Login]]) -> Dict[str, Login]:
        """ Return last login for each user in map"""
        logins_map: Dict[str, Login] = {}
        for key, logins in result.items():
            for login in logins:
                if login.office:
                    logins_map[key] = login
                    break
            if not logins_map.get(key):
                logins_map[key] = logins[0]
        return logins_map

    def get_user_extra_info(self) -> Dict[str, UserExtraInfo]:
        result: Dict[str, Optional[UserExtraInfo]] = {}
        headers = {"Authorization": f"Bearer {self.SLACK_TOKEN}"}
        params = {}
        for users in self._send_users_list_request(params, headers):
            result.update(users)

        return result

    def _send_users_list_request(self, params, headers) -> Generator[Dict[str, UserExtraInfo], None, None]:
        while True:
            result = {}
            resp = requests.get(self.SLACK_USERS_LIST_URL, params=params, headers=headers)
            resp.raise_for_status()
            resp = resp.json()
            if not resp["ok"]:
                return
            for user in resp["members"]:
                extra = UserExtraInfo(email=user["profile"].get("email"), tz=user.get("tz"))
                result[user["id"]] = extra

            next_cursor = resp["response_metadata"].get("cursor")
            params["cursor"] = next_cursor
            yield result

            if not next_cursor:
                return

    def save_to_db(self, filtered):
        con, cursor = get_cursor()
        for login in filtered.values():
            cursor.execute(self.SAVE_QUERY, login.to_dict())
        con.commit()
        cursor.close()
        con.close()


if __name__ == "__main__":
    SlackLogger().run()
