# main.py
import numpy as np
from spotify_utils import (
    create_spotify_client,
    get_all_playlists,
    get_playlist_tracks,
    get_track_audio_features,
    get_track_info,
    create_optimized_playlist,
)
from optimizer import normalize_features, optimize_playlist


def get_user_input(sp) -> str:
    all_playlists = get_all_playlists(sp)

    for id, playlist in enumerate(all_playlists):
        print(f"{id+1}.  {playlist['name']}")

    choice = int(input("Enter the playlist number: "))
    select_playlist = all_playlists[choice - 1]
    print(f"Selected playlist: {select_playlist['name']}")

    return select_playlist["id"]


def main():
    try:
        sp = create_spotify_client()
        playlist_id = get_user_input(sp)
        playlist_tracks = get_playlist_tracks(sp, playlist_id)
        track_ids = [track["track"]["id"] for track in playlist_tracks]
        tracks_audio_features = get_track_audio_features(sp, track_ids)

        song_features = []
        for features in tracks_audio_features:
            if features:
                song_features.append(
                    [
                        features["tempo"],
                        features["key"],
                        features["loudness"],
                        features["danceability"],
                        features["energy"],
                        features["valence"],
                        features["acousticness"],
                        features["instrumentalness"],
                    ]
                )
        song_features = np.array(song_features)
        song_features = normalize_features(song_features)

        optimized_order = optimize_playlist(song_features)
        optimized_track_ids = [track_ids[i] for i in optimized_order]
        optimized_tracks_info = get_track_info(sp, optimized_track_ids)

        print("Optimized Playlist Order:")
        for track in optimized_tracks_info:
            print(
                f"{track['name']} by {' '.join([artist['name'] for artist in track['artists']])} - {track['id']}"
            )

        user_profile = sp.current_user()
        user_id = user_profile["id"]

        new_playlist_id, new_playlist_name = create_optimized_playlist(
            sp, user_id, "My Playlist", optimized_track_ids
        )
        print(
            f"New optimized playlist created: {new_playlist_name} with ID {new_playlist_id}"
        )
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
