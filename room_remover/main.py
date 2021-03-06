import json
import os
from collections import defaultdict
from typing import List, Dict, Tuple

import arrow
from psycopg2.extras import RealDictCursor
from slack_bolt import App

from calendar_listener import CalendarListener
from helpers.db import get_from_db
from helpers.oauth import user_has_auth, get_auth_link

USERS_EVENTS_QUERY = """
SELECT
    e.event_id,
    e.event_start,
    e.event_end,
    e.event_creator,
    e.event_location,
    e.event_location_name,
    sl.office as user_location,
    sl.user_id,
    sl.username,
    sl.email,
    sl.user_tz
FROM calendar_events e
LEFT JOIN (
    SELECT
        user_id,
        username,
        office,
        email,
        user_tz
    FROM
        slack_logins
    WHERE
        pdate = now()::date
    ) sl ON e.event_creator = sl.email
WHERE
    e.event_start::date = now()::date
    and (
        sl.office is null 
        OR lower(sl.office) <> lower(e.event_location)
        )
ORDER BY event_start
"""


class RoomRemover:
    def __init__(self):
        self.slack_app = App(token=os.getenv("SLACK_BOT_TOKEN"), signing_secret=os.getenv("SLACK_SIGNING_SECRET"))
        self.jobs = [CalendarListener()]

    def start_jobs(self):
        for job in self.jobs:
            job.run()

    def run(self):
        self.start_jobs()
        data = get_from_db(USERS_EVENTS_QUERY, cursor_class=RealDictCursor)
        aggregated = self.aggregate_data(data)
        for user_id, events in aggregated.items():
            self.send_slack_message(user_id, events)

    @staticmethod
    def aggregate_data(data: List[Dict]):
        user2event = defaultdict(list)
        for event in data:
            user2event[event["user_id"]].append(event)
        return user2event

    def send_slack_message(self, user_id, events):
        blocks = self.generate_message(user_id, events)
        self.slack_app.client.chat_postMessage(channel=user_id, blocks=blocks)

    def generate_message(self, user_id, events):
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*У тебя сегодня встречи в переговорке, а ты не в офисе* \n Где освободить переговорки?",
                },
            },
            {"type": "divider"},
        ]

        auth_link = None
        if not user_has_auth(user_id):
            auth_link = get_auth_link(user_id)

        for event in events:
            time_from, time_to = self.check_timezone(event)
            value = {
                    "event_id": f"{event['email']}:{event['event_id']}",
                    "room": event['event_location_name'],
                    "time": f"{time_from}-{time_to}",
                    "tz": event.get("user_tz", 'ХЗ')
            }
            accessory = {
                "type": "button",
                "text": {"type": "plain_text", "emoji": True, "text": "Освободить переговорку", },
                "value": json.dumps(value),
                "action_id": "cancel",
            }
            if auth_link:
                accessory["url"] = auth_link

            blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*{time_from}-{time_to}*\n Переговорка: {event['event_location_name']}",
                    },
                    "accessory": accessory,
                }
            )
        return blocks

    @staticmethod
    def check_timezone(event) -> Tuple[str, str]:
        start = event.get("event_start")
        end = event.get("event_end")
        tz = event.get("user_tz")
        if tz:
            time_from = arrow.get(start).to(tz).strftime("%H:%M")
            time_to = arrow.get(end).to(tz).strftime("%H:%M")
        else:
            time_from = start.strftime("%H:%M")
            time_to = end.strftime("%H:%M")
        return time_from, time_to


if __name__ == "__main__":
    RoomRemover().run()
