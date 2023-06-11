# recommender.py

import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity

# Load your DataFrame here
songs_df = pd.read_csv('tracks.csv')

# Select and scale features
features = ['popularity', 'danceability', 'energy', 'loudness', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo']
songs_features = songs_df[features]
scaler = MinMaxScaler()
songs_features_scaled = scaler.fit_transform(songs_features)

# Compute similarity matrix
similarity_matrix = cosine_similarity(songs_features_scaled)

def recommend_songs(song_id, num_songs):
    song_index = songs_df[songs_df['id'] == song_id].index[0]
    similarity_scores = list(enumerate(similarity_matrix[song_index]))
    similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)

    # Get the scores of the num_songs most similar songs
    similarity_scores = similarity_scores[1:num_songs+1]

    # Get the song indices
    song_indices = [i[0] for i in similarity_scores]

    # Return the top num_songs most similar songs
    return songs_df['name'].iloc[song_indices]
