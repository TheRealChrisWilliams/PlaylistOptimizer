import spotipy
from spotipy.oauth2 import SpotifyOAuth
import random
from deap import base, creator, tools, algorithms
import numpy as np
from sklearn.cluster import KMeans

sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id="1561cca081d44aef84347b030c9f0073",
        client_secret="32610111e6ba458ab8a587233ba16da8",
        redirect_uri="http://localhost:8888/callback",
        scope="playlist-read-private playlist-modify-public playlist-modify-private",
    )
)


def get_all_playlists(sp) -> list:
    playlists: list = []
    response = sp.current_user_playlists(limit=50)
    while response:
        playlists.extend(response["items"])
        if response["next"]:
            response = sp.next(response)
        else:
            break
    return playlists


def get_user_input():
    # Fetch all playlists
    all_playlists = get_all_playlists(sp)

    # Print the names of all playlists
    for id, playlist in enumerate(all_playlists):
        print(f"{id+1}.  {playlist['name']}")

    choice = int(input("Enter the playlist number : "))
    select_playlist = all_playlists[choice - 1]  # Select the playlist
    print(f"Selected playlist : {select_playlist['name']}")

    return select_playlist["id"], select_playlist["name"]


def get_playlist_tracks(sp, playlist_id):
    tracks = []
    results = sp.playlist_tracks(playlist_id)
    while results:
        tracks.extend(results["items"])
        if results["next"]:
            results = sp.next(results)
        else:
            results = None
    return tracks


playlist_id, playlist_name = get_user_input()
playlist_tracks = get_playlist_tracks(sp, playlist_id=playlist_id)
track_ids = [track["track"]["id"] for track in playlist_tracks]


def get_track_audio_features(sp: spotipy.Spotify, track_ids: list[str]) -> list[dict]:
    """
    Fetch audio features for the specified tracks from the Spotify API.
    Return a list of dictionaries containing the audio features for each track.
    """
    batch_size = 100  # Spotify API limit for audio_features requests
    tracks_audio_features = []

    for i in range(0, len(track_ids), batch_size):
        batch = track_ids[i : i + batch_size]
        try:
            batch_features = sp.audio_features(batch)
            tracks_audio_features.extend(batch_features)
        except spotipy.exceptions.SpotifyException as e:
            print(f"Error fetching audio features for batch: {e}")

    return tracks_audio_features


tracks_audio_features = get_track_audio_features(sp, track_ids)

song_features = []
for features in tracks_audio_features:
    if features:  # Ensure the track has features available
        # Now including danceability, energy, valence, acousticness, and instrumentalness
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
print(song_features)

# Normalize features (simple min-max scaling)
min_vals = song_features.min(axis=0)
max_vals = song_features.max(axis=0)
song_features = (song_features - min_vals) / (max_vals - min_vals)


def cluster_tracks(song_features, num_clusters=5):
    kmeans = KMeans(n_clusters=num_clusters, random_state=42)
    labels = kmeans.fit_predict(song_features)
    return labels


# Preparing the genetic algorithm environment
creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", list, fitness=creator.FitnessMin)

toolbox = base.Toolbox()
toolbox.register("mate", tools.cxOrdered)
toolbox.register("mutate", tools.mutShuffleIndexes, indpb=0.05)
toolbox.register("select", tools.selTournament, tournsize=3)


# Evaluation function
def evaluate(individual):
    distances = np.linalg.norm(
        song_features[individual[:-1]] - song_features[individual[1:]], axis=1
    )
    return (np.sum(distances),)


toolbox.register("evaluate", evaluate)


# Running GA on a cluster
def optimize_cluster(cluster_song_features):
    cluster_size = len(cluster_song_features)
    toolbox.register("attribute", random.sample, range(cluster_size), cluster_size)
    toolbox.register(
        "individual", tools.initIterate, creator.Individual, toolbox.attribute
    )
    toolbox.register("population", tools.initRepeat, list, toolbox.individual, n=100)

    pop = toolbox.population()
    hof = tools.HallOfFame(1, similar=np.array_equal)
    algorithms.eaSimple(
        pop,
        toolbox,
        cxpb=0.7,
        mutpb=0.2,
        ngen=50,
        stats=None,
        halloffame=hof,
        verbose=False,
    )

    return [cluster_song_features[i] for i in hof[0]]


# Main function
def main(song_features):
    # Cluster songs
    labels = cluster_tracks(song_features)
    clusters = [[] for _ in range(max(labels) + 1)]
    for i, label in enumerate(labels):
        clusters[label].append(i)

    # Optimize order within each cluster
    optimized_clusters = [optimize_cluster(cluster) for cluster in clusters]

    # Flatten the cluster order for a final optimization run
    flat_optimized_clusters = [
        song for cluster in optimized_clusters for song in cluster
    ]
    global_optimized_order = optimize_cluster(flat_optimized_clusters)

    return global_optimized_order


# Example usage
# Ensure song_features is defined and normalized before this
optimized_order = main(song_features)

# Print the optimized playlist order
print("Optimized Playlist Order:")
print(optimized_order)


def get_track_info(sp, track_ids):
    """
    Fetch and return track information for the given track IDs.
    """
    batch_size = 50  # Spotify API limit for tracks requests
    track_info = []

    for i in range(0, len(track_ids), batch_size):
        batch = track_ids[i : i + batch_size]
        try:
            batch_info = sp.tracks(batch)["tracks"]
            track_info.extend(batch_info)
        except spotipy.exceptions.SpotifyException as e:
            print(f"Error fetching track information for batch: {e}")

    return track_info


# Assuming track_ids and optimized_order are available
optimized_track_ids = [track_ids[i] for i in optimized_order]
optimized_tracks_info = get_track_info(sp, optimized_track_ids)

print("Optimized Playlist Order:")
for track in optimized_tracks_info:
    print(
        f"{track['name']} by {' '.join([artist['name'] for artist in track['artists']])} - {track['id']}"
    )


def create_optimized_playlist(sp, user_id, playlist_name, track_ids):
    # Create a new playlist
    new_playlist = sp.user_playlist_create(
        user_id, f"{playlist_name} Optimized(TM)", public=False
    )
    new_playlist_id = new_playlist["id"]

    # Add tracks to the new playlist in batches of 100 (Spotify's limit)
    for i in range(0, len(track_ids), 100):
        batch = track_ids[i : i + 100]
        sp.user_playlist_add_tracks(user_id, new_playlist_id, batch)

    return new_playlist_id


# Fetch the current user's profile to get their user ID
user_profile = sp.current_user()
user_id = user_profile["id"]

# Call the function to create the new playlist and add optimized tracks
new_playlist_id = create_optimized_playlist(
    sp, user_id, playlist_name, optimized_track_ids
)
print(
    f"New optimized playlist created: {playlist_name} Optimized(TM) with ID {new_playlist_id}"
)
