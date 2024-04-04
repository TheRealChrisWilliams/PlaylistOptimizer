# playlist_optimizer.py
import numpy as np
from sklearn.cluster import KMeans
from deap import base, creator, tools, algorithms
import random
from typing import List, Tuple

def normalize_features(song_features: np.ndarray) -> np.ndarray:
    min_vals = song_features.min(axis=0)
    max_vals = song_features.max(axis=0)
    return (song_features - min_vals) / (max_vals - min_vals)

def cluster_tracks(song_features: np.ndarray, num_clusters: int = 5) -> List[int]:
    kmeans = KMeans(n_clusters=num_clusters, random_state=42)
    labels = kmeans.fit_predict(song_features)
    return labels.tolist()

# Preparing the genetic algorithm environment
creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", list, fitness=creator.FitnessMin)

toolbox = base.Toolbox()
toolbox.register("mate", tools.cxOrdered)
toolbox.register("mutate", tools.mutShuffleIndexes, indpb=0.05)
toolbox.register("select", tools.selTournament, tournsize=3)

def evaluate(individual: List[int], song_features: np.ndarray) -> Tuple[float]:
    distances = np.linalg.norm(
        song_features[individual[:-1]] - song_features[individual[1:]], axis=1
    )
    return (np.sum(distances),)

def optimize_cluster(cluster_song_features: np.ndarray) -> List[int]:
    cluster_size = len(cluster_song_features)
    toolbox.register("attribute", random.sample, range(cluster_size), cluster_size)
    toolbox.register(
        "individual", tools.initIterate, creator.Individual, toolbox.attribute
    )
    toolbox.register("population", tools.initRepeat, list, toolbox.individual, n=100)

    # Register the evaluate function with the song_features argument
    toolbox.decorate("evaluate", evaluate, song_features=cluster_song_features)

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

def optimize_playlist(song_features: np.ndarray) -> List[int]:
    # Cluster songs
    labels = cluster_tracks(song_features)
    clusters = [[] for _ in range(max(labels) + 1)]
    for i, label in enumerate(labels):
        clusters[label].append(i)

    # Optimize order within each cluster
    optimized_clusters = [optimize_cluster(song_features[cluster]) for cluster in clusters]

    # Flatten the cluster order for a final optimization run
    flat_optimized_clusters = [
        song for cluster in optimized_clusters for song in cluster
    ]
    global_optimized_order = optimize_cluster(flat_optimized_clusters)

    return global_optimized_order