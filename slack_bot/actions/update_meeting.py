import json

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from slack_bot.actions.oauth import get_credentials


def remove_meeting_room(user_id, calendar_id, meeting_id):
    credentials = get_credentials(user_id)

    service = build('calendar', 'v3', credentials=credentials)

    try:
        event = service.events().get(calendarId=calendar_id, eventId=meeting_id).execute()
        # event not found?
    except HttpError as e:
        print(e)
        return

    # Remove location
    event['location'] = ""
    event['attendees'] = [_ for _ in event.get('attendees', []) if not _.get('resource')]

    # Patch event
    result = service.events().patch(calendarId=calendar_id, eventId=meeting_id, body=event).execute()

    return result


def get_event_info(actions):
    for action in actions:
        if action['action_id'] == 'cancel':
            return json.loads(action['value'])
