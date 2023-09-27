import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv
from os.path import join, dirname

# .env
load_dotenv(verbose=True)
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

# Recommendations -> CSV
def recommendations_to_csv(recommendations):
    recommended_songs = pd.DataFrame(columns=['Song', 'Artist'])
    for track in recommendations['tracks']:
        recommended_songs = recommended_songs.append({'Song': track['name'], 'Artist': track['artists'][0]['name']}, ignore_index=True)
    recommended_songs.to_csv('recommended_songs.csv', index=False)


client_id = os.environ.get("SPOTIFY_CLIENT_ID")
client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET")
redirect_uri = "http://127.0.0.1:8080/"
scope = "playlist-modify-public"
spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, scope=scope))

# song_idを入力してもらう
@st.cache
def song_id():
    song_id = st.text_input("Enter song ID")
    return song_id

# プレイリストの名前を入力してもらう
@st.cache
def playlist_name():
    playlist_name = st.text_input("Enter playlist name: ")
    return playlist_name

@st.cache
# argument:song_id -> features
def get_features(song_id):
    features = spotify.audio_features(song_id)[0]
    return features, song_id

@st.cache
# argument:features -> recommendations
def get_recommendations(features,song_id):
    recommendations = spotify.recommendations(seed_tracks=[song_id], limit=15, target_energy=features['energy']+0.05, target_danceability=features['danceability'])
    return recommendations

@st.cache
# Create new playlist
def create_playlist(name, recommendations):
    playlist_name = name
    user_id = spotify.current_user()["id"]
    playlist = spotify.user_playlist_create(user_id,playlist_name)
    track_ids = [track['id'] for track in recommendations["tracks"]]
    spotify.playlist_add_items(playlist["id"],track_ids)
    print("New playlist created: ", playlist_name)


# Title
st.title('Spotify Autoplaylist')
st.header('This is a header')
st.subheader('This is a subheader')
st.text('This is some text.')
song_id = st.text_input("Enter song ID")
playlist_name = st.text_input("Enter playlist name: ")

features, song_id = get_features(song_id)
recommendations = get_recommendations(features,song_id)
create_playlist(playlist_name, recommendations)


