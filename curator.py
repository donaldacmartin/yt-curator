from sys import argv, exit

from service.local import load_subscriptions, save_subscriptions
from service.playlist import create_yt_playlist, add_to_playlist
from service.subscription import get_yt_subscriptions, get_videos_for_subscriptions
from service.repo import get_authenticated_service


REFRESH_SUBS = "--refresh-subscriptions"
CREATE_PLAYLIST = "--create-playlist"
MODES = [REFRESH_SUBS, CREATE_PLAYLIST]

CHANNEL = "channelId"


def print_usage():
    print("Usage:")
    print("--refresh-subscriptions    Adds/removes subscriptions from the CSV")
    print("--create-playlist          Creates a playlist from the existing CSV")


def refresh_subscriptions(service):
    print("Calling YouTube for subscriptions")
    yt_subs = get_yt_subscriptions(service)
    local_subs = load_subscriptions()

    yt_sub_ids = set([s[CHANNEL] for s in yt_subs])
    local_sub_ids = set([s[CHANNEL] for s in local_subs])

    new_ids = yt_sub_ids.difference(local_sub_ids)
    new_subs = [sub for sub in yt_subs if sub[CHANNEL] in new_ids]

    refreshed_subs = local_subs + new_subs

    save_subscriptions(refreshed_subs)
    print("Saved %d new subscriptions" % len(new_ids))


def create_playlist(service):
    subscriptions = load_subscriptions()
    print("Loaded %d subscriptions" % len(subscriptions))
    videos = get_videos_for_subscriptions(subscriptions, service)

    if len(videos) < 1:
        print("No videos to add")
        exit(0)
    else:
        print("Creating playlist")
        playlist_id = create_yt_playlist(youtube)

        print("Appending %d video(s) to playlist" % len(videos))
        [add_to_playlist(playlist_id, video, service) for video in videos]

        print("Done")
        exit(0)


if __name__ == "__main__":
    if len(argv) < 2 or argv[1] not in MODES:
        print_usage()
        exit(0)

    youtube = get_authenticated_service()
    mode = argv[1]

    if mode == REFRESH_SUBS:
        refresh_subscriptions(youtube)
    elif mode == CREATE_PLAYLIST:
        create_playlist(youtube)
