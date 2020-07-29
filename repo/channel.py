CONTENT = "contentDetails"
PLAYLISTS = "relatedPlaylists"
UPLOADS = "uploads"
ITEMS = "items"
NEXT_PAGE = "nextPageToken"


def get_playlists(channel_ids, service):
    channel_id = ",".join(channel_ids)
    info = _get_channel_info(channel_id, service)
    details = [channel[CONTENT] for channel in info if CONTENT in channel]
    playlists = [detail[PLAYLISTS] for detail in details if PLAYLISTS in detail]
    return [playlist[UPLOADS] for playlist in playlists if UPLOADS in playlist]


def _get_channel_info(channel_id, service, page_token=""):
    params = {
        "part": "contentDetails",
        "id": channel_id,
        "maxResults": 50,
        "pageToken": page_token
    }

    response = service.channels().list(**params).execute()
    items = response[ITEMS] if ITEMS in response else []

    if NEXT_PAGE in response:
        return items + _get_channel_info(service, response[NEXT_PAGE])
    else:
        return items
