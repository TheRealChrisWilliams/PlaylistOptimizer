# spotify_utils.py
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from config import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, SCOPE
from typing import List, Dict, Tuple

def create_spotify_client() -> spotipy.Spotify:
    try:
        sp = spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                client_id=CLIENT_ID,
                client_secret=CLIENT_SECRET,
                redirect_uri=REDIRECT_URI,
                scope=SCOPE,
            )
        )
        return sp
    except Exception as e:
        print(f"Error creating Spotify client: {e}")
        raise e

def get_all_playlists(sp: spotipy.Spotify) -> List[Dict]:
    try:
        playlists = []
        response = sp.current_user_playlists(limit=50)
        while response:
            playlists.extend(response["items"])
            if response["next"]:
                response = sp.next(response)
            else:
                break
        return playlists
    except Exception as e:
        print(f"Error fetching playlists: {e}")
        raise e

def get_playlist_tracks(sp: spotipy.Spotify, playlist_id: str) -> List[Dict]:
    try:
        tracks = []
        results = sp.playlist_tracks(playlist_id)
        while results:
            tracks.extend(results["items"])
            if results["next"]:
                results = sp.next(results)
            else:
                results = None
        return tracks
    except Exception as e:
        print(f"Error fetching playlist tracks: {e}")
        raise e

def get_track_audio_features(sp: spotipy.Spotify, track_ids: List[str]) -> List[Dict]:
    try:
        batch_size = 100
        tracks_audio_features = []

        for i in range(0, len(track_ids), batch_size):
            batch = track_ids[i : i + batch_size]
            batch_features = sp.audio_features(batch)
            tracks_audio_features.extend(batch_features)

        return tracks_audio_features
    except Exception as e:
        print(f"Error fetching audio features for tracks: {e}")
        raise e

def get_track_info(sp: spotipy.Spotify, track_ids: List[str]) -> List[Dict]:
    try:
        batch_size = 50
        track_info = []

        for i in range(0, len(track_ids), batch_size):
            batch = track_ids[i : i + batch_size]
            batch_info = sp.tracks(batch)["tracks"]
            track_info.extend(batch_info)

        return track_info
    except Exception as e:
        print(f"Error fetching track information: {e}")
        raise e

def create_optimized_playlist(
    sp: spotipy.Spotify, user_id: str, playlist_name: str, track_ids: List[str]
) -> Tuple[str, str]:
    try:
        new_playlist = sp.user_playlist_create(
            user_id, f"{playlist_name} Optimized(TM)", public=False
        )
        new_playlist_id = new_playlist["id"]

        for i in range(0, len(track_ids), 100):
            batch = track_ids[i : i + 100]
            sp.user_playlist_add_tracks(user_id, new_playlist_id, batch)

        return new_playlist_id, f"{playlist_name} Optimized(TM)"
    except Exception as e:
        print(f"Error creating optimized playlist: {e}")
        raise e