import os
import requests
from flask import Flask, render_template, redirect, request
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from config import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Spotify OAuth configuration
sp_oauth = SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope="playlist-read-private playlist-modify-public playlist-modify-private"
)

@app.route('/')
def index():
    auth_url = sp_oauth.get_authorize_url()
    print(f"Generated auth URL: {auth_url}")
    try:
        response = requests.get(auth_url)
        if response.status_code == 200:
            print("Auth URL is valid and accessible.")
        else:
            print(f"Error accessing auth URL: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error accessing auth URL: {e}")
    return render_template('index.html', auth_url=auth_url)

@app.route('/callback/')
def callback():
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    access_token = token_info['access_token']

    # Create a Spotify client with the access token
    sp = spotipy.Spotify(auth=access_token)

    # Fetch the user's profile information
    user_profile = sp.current_user()
    display_name = user_profile['display_name']

    return f"Welcome, {display_name}! You have successfully authenticated with Spotify."

if __name__ == '__main__':
    app.run(debug=True)