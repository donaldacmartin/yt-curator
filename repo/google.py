from os.path import exists
from pickle import load, dump
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


SECRETS = "secrets.json"
TOKEN_FILE = "token.pickle"
SCOPES = ["https://www.googleapis.com/auth/youtube"]
API_SERVICE = "youtube"
API_VERSION = "v3"


def get_authenticated_service():
    credentials = None

    if exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            credentials = load(token)

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(SECRETS, SCOPES)
            credentials = flow.run_local_server(port=0)

        with open('token.pickle', 'wb') as token:
            dump(credentials, token)

    return build(API_SERVICE, API_VERSION, credentials=credentials)
