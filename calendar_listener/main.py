import json

import arrow

from config import settings
from helpers.db import get_cursor
from calendar_listener.utils import get_service

RFC3339 = "YYYY-MM-DDT00:00:00Z"


def get_calendars():
    with open(f'{settings.BASE_DIR}/calendar_listener/calendars.json', 'r') as _file:
        return json.load(_file)


def get_period():
    today = arrow.utcnow()
    today_string = today.format(RFC3339)
    tomorrow_string = today.shift(days=1).format(RFC3339)

    return today_string, tomorrow_string


def get_calendar_events(calendar, service):
    # Получаем все эвенты на текущий день
    today_string, tomorrow_string = get_period()

    results = service.events().list(calendarId=calendar['id'], timeMin=today_string, timeMax=tomorrow_string).execute()
    return results.get('items', [])


def export_calendar_events_to_file(calendar, events):
    with open("%s.json" % calendar['id'], 'w') as _file:
        json.dump(events, _file, indent=4, ensure_ascii=False)


def delete_today_events():
    today_string, tomorrow_string = get_period()
    query_template = """DELETE FROM calendar_events WHERE event_start >= %(today)s AND event_start < %(tomorrow)s;"""

    c, cursor = get_cursor()
    cursor.execute(query_template, {'today': today_string, 'tomorrow': tomorrow_string})
    c.commit()
    cursor.close()
    c.close()


def export_calendar_events(calendar, events):
    def map_event(event):
        return {
            'id': event['id'],
            'event_start': arrow.get(event['start']['dateTime']).to('UTC').format(arrow.FORMAT_W3C),
            'event_end': arrow.get(event['end']['dateTime']).to('UTC').format(arrow.FORMAT_W3C),
            'event_creator': event['creator']['email'],
            'event_location': calendar['location'],
            'event_location_name': calendar['summary']
        }

    c, cursor = get_cursor()

    query_template = """INSERT INTO calendar_events(event_id, event_start, event_end, event_creator, event_location, event_location_name)
                        VALUES %s
                        ON CONFLICT ON CONSTRAINT calendar_events_event_id_key 
                        DO NOTHING;"""
    params_template = """(%(id)s, %(event_start)s, %(event_end)s, %(event_creator)s, %(event_location)s, %(event_location_name)s)"""
    insert_params = ",".join(cursor.mogrify(params_template, x).decode() for x in map(map_event, events))
    cursor.execute(query_template % insert_params)
    c.commit()

    cursor.close()
    c.close()


class CalendarListener:

    @staticmethod
    def run():
        # Получаем календари из конфига
        calendars = get_calendars()
        service = get_service()

        # Очищаем эвенты на сегодня
        delete_today_events()

        for calendar in calendars:
            # Получаем эвенты для календаря
            events = get_calendar_events(calendar, service)

            # Экспортируем эвенты в базу
            if events:
                export_calendar_events(calendar, events)


if __name__ == '__main__':
    CalendarListener().run()
