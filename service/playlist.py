from datetime import date, datetime, timedelta
from service.repo import (list_channel_info,
                          list_playlist_items,
                          create_playlist,
                          add_to_playlist)


CONTENT = "contentDetails"
PLAYLISTS = "relatedPlaylists"
UPLOADS = "uploads"
SNIPPET = "snippet"
CHANNEL = "channelId"
RESOURCE = "resourceId"
VIDEO = "videoId"
PUBLISHED_AT = "publishedAt"

ISO_8601 = "%Y-%m-%dT%H:%M:%SZ"
PLAYLIST_NAME_FORMAT = "%a %-d %b %Y"
ONE_DAY = timedelta(days=1)


def get_playlists(channel_ids, service):
    channel_id = ",".join(channel_ids)
    channel_info_response = list_channel_info(channel_id, service)
    playlists = _extract_playlists(channel_info_response)
    return list(set(playlists))


def get_playlist_videos(playlist_id, service):
    playlist_items_response = list_playlist_items(playlist_id, service)
    return _extract_videos(playlist_items_response)


def create_yt_playlist(service):
    title = date.today().strftime(PLAYLIST_NAME_FORMAT)
    return create_playlist(title, service)


def add_video_to_playlist(playlist_id, video_id, service):
    return add_to_playlist(playlist_id, video_id, service)


def _extract_playlists(response):
    details = [channel[CONTENT] for channel in response if CONTENT in channel]
    playlists = [detail[PLAYLISTS] for detail in details if PLAYLISTS in detail]
    return [playlist[UPLOADS] for playlist in playlists if UPLOADS in playlist]


def _extract_videos(response):
    snippets = [item[SNIPPET] for item in response if SNIPPET in item]
    today_only = [snip for snip in snippets if _is_last_day(snip)]
    resources = [(snip[CHANNEL], snip[RESOURCE]) for snip in today_only]
    return [(channel, resource[VIDEO]) for channel, resource in resources]


def _is_last_day(snippet):
    if PUBLISHED_AT in snippet:
        published_at = snippet[PUBLISHED_AT]
        published_date = datetime.strptime(published_at, ISO_8601)
        cut_off_date = datetime.utcnow() - ONE_DAY
        return published_date >= cut_off_date

    return False
