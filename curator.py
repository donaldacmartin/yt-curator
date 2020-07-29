from sys import exit

from repo.google import get_authenticated_service
from repo.local import load_subscriptions, save_subscriptions
from repo.playlist import create_playlist, add_to_playlist
from repo.subscription import get_my_subscriptions, get_videos_for_subscriptions


def get_subscriptions(service):
    subscriptions = load_subscriptions()

    if subscriptions is None:
        print("Getting subscriptions from YouTube")
        subscriptions = get_my_subscriptions(service)
        save_subscriptions(subscriptions)
    else:
        print("Loaded %d subscriptions from file" % len(subscriptions))

    return subscriptions


if __name__ == "__main__":
    youtube = get_authenticated_service()
    subscriptions = get_subscriptions(youtube)

    print("Getting videos for each subscription")
    videos = get_videos_for_subscriptions(subscriptions, youtube)

    if len(videos) < 1:
        print("No videos to add")
        exit(0)
    else:
        print("Creating playlist")
        playlist_id = create_playlist(youtube)

        print("Appending videos to playlist")
        [add_to_playlist(playlist_id, video, youtube) for video in videos]

        print("Done")
        exit(0)
