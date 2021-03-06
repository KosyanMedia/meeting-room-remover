import os
import pickle
import sys

from googleapiclient.discovery import build

from config import settings


def get_service():
    if os.path.exists(f'{settings.BASE_DIR}/calendar_listener/token.pickle'):
        with open(f'{settings.BASE_DIR}/calendar_listener/token.pickle', 'rb') as token:
            creds = pickle.load(token)
    else:
        print("Failed to load tocken.pickle")
        sys.exit(1)

    return build('calendar', 'v3', credentials=creds)
