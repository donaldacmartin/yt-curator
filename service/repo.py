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

ITEMS = "items"
NEXT_PAGE = "nextPageToken"
RESULTS_PER_PAGE = 50
SNIPPET = "snippet"
ID = "id"
PLAYLIST = "playlistId"
RESOURCE = "resourceId"
VIDEO = "videoId"
KIND = "kind"
VIDEO_KIND = "youtube#video"


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


def list_subscriptions(service, page_token=""):
    params = {
        "part": "snippet",
        "mine": True,
        "maxResults": RESULTS_PER_PAGE,
        "pageToken": page_token
    }

    response = service.subscriptions().list(**params).execute()
    items = response[ITEMS] if ITEMS in response else []

    if NEXT_PAGE in response:
        return items + list_subscriptions(service, response[NEXT_PAGE])
    else:
        return items


def list_channel_info(channel_id, service, page_token=""):
    params = {
        "part": "contentDetails",
        "id": channel_id,
        "maxResults": RESULTS_PER_PAGE,
        "pageToken": page_token
    }

    response = service.channels().list(**params).execute()
    items = response[ITEMS] if ITEMS in response else []

    if NEXT_PAGE in response:
        return items + list_channel_info(service, response[NEXT_PAGE])
    else:
        return items


def list_playlist_items(playlist_id, service, page_token=""):
    params = {
        "part": "snippet",
        "playlistId": playlist_id,
        "maxResults": 50,
        "pageToken": page_token
    }

    response = service.playlistItems().list(**params).execute()
    items = response[ITEMS] if ITEMS in response else []

    if NEXT_PAGE in response:
        return items + list_playlist_items(playlist_id, service, response[NEXT_PAGE])
    else:
        return items


def create_playlist(title, service):
    body = {SNIPPET: {"title": title}}
    response = service.playlists().insert(part=SNIPPET, body=body).execute()
    return response[ID] if ID in response else None


def add_to_playlist(playlist_id, video_id, service):
    resource = {KIND: VIDEO_KIND, VIDEO: video_id}
    snippet = {PLAYLIST: playlist_id, RESOURCE: resource}
    body = {SNIPPET: snippet}
    response = service.playlistItems().insert(part=SNIPPET, body=body).execute()
    return response
