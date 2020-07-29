from datetime import date, datetime, timedelta


SNIPPET = "snippet"
CHANNEL = "channelId"
PLAYLIST = "playlistId"
RESOURCE = "resourceId"
VIDEO = "videoId"
KIND = "kind"
VIDEO_KIND = "youtube#video"
ITEMS = "items"
NEXT_PAGE = "nextPageToken"
PUBLISHED_AT = "publishedAt"
ID = "id"

ISO_8601 = "%Y-%m-%dT%H:%M:%SZ"
PLAYLIST_NAME_FORMAT = "%a %-d %b %Y"
ONE_DAY = timedelta(days=1)


def get_playlist_videos(playlist_id, service):
    items = _get_playlist_items(playlist_id, service)
    snippets = [item[SNIPPET] for item in items if SNIPPET in item]
    today_snippets = [snippet for snippet in snippets if _is_last_day(snippet)]
    resources = [(snippet[CHANNEL], snippet[RESOURCE]) for snippet in today_snippets]
    return [(channel, resource[VIDEO]) for channel, resource in resources]


def create_playlist(service):
    title = date.today().strftime(PLAYLIST_NAME_FORMAT)
    body = {SNIPPET: {"title": title}}
    response = service.playlists().insert(part=SNIPPET, body=body).execute()
    return response[ID] if ID in response else None


def add_to_playlist(playlist_id, video_id, service):
    resource = {KIND: VIDEO_KIND, VIDEO: video_id}
    snippet = {PLAYLIST: playlist_id, RESOURCE: resource}
    body = {SNIPPET: snippet}
    response = service.playlistItems().insert(part=SNIPPET, body=body).execute()
    return response


def _get_playlist_items(playlist_id, service, page_token=""):
    params = {
        "part": "snippet",
        "playlistId": playlist_id,
        "maxResults": 50,
        "pageToken": page_token
    }

    response = service.playlistItems().list(**params).execute()
    items = response[ITEMS] if ITEMS in response else []

    if NEXT_PAGE in response:
        return items + _get_playlist_items(playlist_id, service, response[NEXT_PAGE])
    else:
        return items


def _is_last_day(snippet):
    if PUBLISHED_AT in snippet:
        published_at = snippet[PUBLISHED_AT]
        published_date = datetime.strptime(published_at, ISO_8601)
        cut_off_date = datetime.utcnow() - ONE_DAY
        return published_date >= cut_off_date

    return False
