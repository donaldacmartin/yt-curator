from service.playlist import get_playlists, get_playlist_videos
from service.repo import list_subscriptions


GRP_LEN = 50

SNIPPET = "snippet"
TITLE = "title"
RESOURCE = "resourceId"
CHANNEL = "channelId"


def get_yt_subscriptions(service):
    subscription_response = list_subscriptions(service)
    subscriptions = _extract_subs_from(subscription_response)
    return _no_duplicate_subscriptions(subscriptions)


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


def _extract_subs_from(response):
    snippets = [sub[SNIPPET] for sub in response if SNIPPET in sub]
    resources = [(snip[TITLE], snip[RESOURCE]) for snip in snippets]
    return [{CHANNEL: res[CHANNEL], TITLE: title} for title, res in resources]


def _no_duplicate_subscriptions(subscriptions):
    encountered_channels = set()
    unique_list = []

    for sub in subscriptions:
        if sub[CHANNEL] not in encountered_channels:
            unique_list.append(sub)
            encountered_channels.add(sub[CHANNEL])

    return unique_list


def _no_duplicates(videos):
    encountered_videos = set()
    no_duplicate_videos = []

    for video in videos:
        if video not in encountered_videos:
            no_duplicate_videos.append(video)
            encountered_videos.add(video)

    return no_duplicate_videos
