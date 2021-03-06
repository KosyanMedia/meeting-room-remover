import os
import pickle

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/calendar.events'
]

CREDENTIALS_PATH = os.getenv('GOOGLE_CREDENTIALS_PATH')
TOKEN_PATH = os.getenv('TOKEN_PATH')
REDIRECT_URL = os.getenv('REDIRECT_URL')


def get_credentials(user_id):
    token_file = "%s_token.pickle" % user_id
    token_filepath = os.path.join(TOKEN_PATH, token_file)
    if os.path.exists(token_filepath):
        with open(token_filepath, 'rb') as token:
            user_credentials = pickle.load(token)

            return user_credentials


def is_valid_auth(credentials):
    if credentials is None:
        return False
    # If there are no (valid) credentials available, let the user log in.
    elif not credentials or not credentials.valid:
        return False

    return True


def update_credentials(user_id, credentials):
    token_file = "%s_token.pickle" % user_id
    token_filepath = os.path.join(TOKEN_PATH, token_file)
    with open(token_filepath, 'wb') as token:
        pickle.dump(credentials, token)


def user_has_auth(user_id):
    user_credentials = get_credentials(user_id)

    # If there are no (valid) credentials available, let the user log in.
    if not is_valid_auth(user_credentials):
        if user_credentials and user_credentials.expired and user_credentials.refresh_token:
            user_credentials.refresh(Request())
            # Save the credentials for the next run
            update_credentials(user_id, user_credentials)
            return True
        else:
            return False

    return True


def get_auth_link(user_id):
    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES,
                                                     redirect_uri=REDIRECT_URL,
                                                     state=user_id)
    auth_url, _ = flow.authorization_url(prompt='consent')

    return auth_url


def update_token(user_id, code):
    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES,
                                                     redirect_uri=REDIRECT_URL,
                                                     state=user_id)
    flow.fetch_token(code=code)

    update_credentials(user_id, flow.credentials)
