from repo.channel import get_playlists
from repo.playlist import get_playlist_videos


GRP_LEN = 50

SNIPPET = "snippet"
TITLE = "title"
RESOURCE = "resourceId"
CHANNEL = "channelId"
ITEMS = "items"
NEXT_PAGE = "nextPageToken"


def get_my_subscriptions(service):
    subscriptions = _get_subscriptions(service)
    snippets = [sub[SNIPPET] for sub in subscriptions if SNIPPET in sub]
    resources = [(snip[TITLE], snip[RESOURCE]) for snip in snippets]
    subs = [{CHANNEL: res[CHANNEL], TITLE: title} for title, res in resources]
    return _no_dupe_subs(subs)


def get_videos_for_subscriptions(subscriptions, service):
    channels = [subscription[CHANNEL] for subscription in subscriptions]

    groups = [channels[i:i + GRP_LEN] for i in range(0, len(channels), GRP_LEN)]
    group_playlists = [get_playlists(group, service) for group in groups]

    playlists = [playlist for group in group_playlists for playlist in group]
    playlist_items = [get_playlist_videos(p, service) for p in playlists]

    all_channel_videos = [y for x in playlist_items for y in x]
    videos_by_channel = {chan: [] for chan, _ in all_channel_videos}
    [videos_by_channel[chan].append(vid) for chan, vid in all_channel_videos]

    vids_by_channel = {x: y for x, y in videos_by_channel.items() if len(y) > 0}
    vid_channels = vids_by_channel.keys()
    ordered_channel_ids = [sub[CHANNEL] for sub in subscriptions if sub[CHANNEL] in vid_channels]

    ordered_vid_grps = [videos_by_channel[c_id] for c_id in ordered_channel_ids]
    ordered_vids = [x for y in ordered_vid_grps for x in y]

    return _no_duplicates(ordered_vids)


def _get_subscriptions(service, page_token=""):
    params = {
        "part": "snippet",
        "mine": True,
        "maxResults": 50,
        "pageToken": page_token
    }

    response = service.subscriptions().list(**params).execute()
    items = response[ITEMS] if ITEMS in response else []

    if NEXT_PAGE in response:
        return items + _get_subscriptions(service, response[NEXT_PAGE])
    else:
        return items


def _no_dupe_subs(subscriptions):
    encountered_channels = set()
    no_dup_subs = []

    for sub in subscriptions:
        if sub[CHANNEL] not in encountered_channels:
            no_dup_subs.append(sub)
            encountered_channels.add(sub[CHANNEL])

    return no_dup_subs


def _no_duplicates(videos):
    encountered_videos = set()
    no_duplicate_videos = []

    for video in videos:
        if video not in encountered_videos:
            no_duplicate_videos.append(video)
            encountered_videos.add(video)

    return no_duplicate_videos
