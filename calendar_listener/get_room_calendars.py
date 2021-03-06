import json

from calendar_listener.utils import get_service
from config import settings


def main():
    service = get_service()
    results = service.calendarList().list().execute()

    calendars = []
    for item in results.get('items', []):
        if [location for location in ['hkt', 'mow', 'spb'] if location in item['summary'].lower()]:
            calendars.append({
                'location': item['summary'].split('-')[0].lower(),
                'id': item['id'],
                'summary': item['summary'],
            })

    with open(f'{settings.BASE_DIR}/calendars.json', 'w') as _file:
        json.dump(calendars, _file, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    main()
