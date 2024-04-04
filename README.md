# Playlist Optimizer

The Playlist Optimizer is a sophisticated tool designed to enhance your music listening experience on Spotify. Utilizing advanced data science techniques, including clustering algorithms and genetic algorithms (GAs), this optimizer rearranges your selected Spotify playlist into an order that ensures a smooth and engaging listening journey.

## Features

- **Spotify Integration**: Seamlessly connects with your Spotify account to access your playlists and track features.
- **Audio Feature Analysis**: Leverages Spotify's rich set of audio features for each track, such as tempo, energy, danceability, valence, acousticness, and instrumentalness, to understand the musical characteristics of each song in your playlist.
- **Clustering Algorithm**: Groups songs into clusters based on similarity in their audio features, ensuring that songs within the same cluster have a similar vibe or energy level.
- **Genetic Algorithm Optimization**: Within each cluster, a genetic algorithm optimizes the order of songs to ensure smooth transitions based on their audio features. After optimizing song order within clusters, the GA then determines the optimal sequence of these clusters to form the final playlist.
- **Custom Playlist Creation**: Automatically generates a new Spotify playlist titled "{original_playlist_name} Optimized(TM)" containing the songs from your selected playlist in their newly optimized order.

## How It Works

1. **Clustering Phase**: The tool starts by analyzing the audio features of each track in the selected playlist and groups them into clusters of similar songs. This step reduces the complexity of the optimization process by focusing on smaller, more homogeneous groups of songs.

2. **GA Within Clusters**: For each cluster, the tool runs a genetic algorithm to find the best order of songs, optimizing for smooth transitions based on their audio features.

3. **Final GA Run**: Treats each optimized cluster as a single unit and uses another genetic algorithm to optimize the order of these clusters, considering the overall flow and progression of the playlist.

4. **Playlist Creation**: Once the final order is determined, the tool creates a new Spotify playlist with your songs arranged in this optimized order, ready for you to enjoy.

## Technical Overview

- **Spotify API**: Fetches playlists, tracks, and audio features from your Spotify account.
- **K-Means Clustering**: Groups tracks into clusters based on their audio features to simplify the optimization process.
- **Genetic Algorithms**: Used to optimize the song order within each cluster and the sequence of clusters to ensure a cohesive and enjoyable listening experience.
- **Python Libraries**: The tool is built using Python, with libraries such as Spotipy for Spotify API interactions, DEAP for genetic algorithms, and Scikit-learn for clustering.

This Playlist Optimizer offers a unique way to rediscover and enjoy your favorite Spotify playlists, ensuring every listening session is as engaging and enjoyable as possible.
