import API_config
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import json
import pandas as pd

client_id = f"API_config.client_id"
client_secret = f"API_config.client_secret"
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Line below is for Top 50 Global songs
playlist_link = "https://open.spotify.com/playlist/37i9dQZEVXbNG2KDcFcKOF?si=3ba7f1262cdb41aa"
playlist_URI = playlist_link.split("/")[-1].split("?")[0]
data = sp.playlist_items(playlist_URI)

# dump the data to a JSON file
json_file_path = "spotify_data.json"

with open(json_file_path, 'w', encoding='utf-8') as json_file:
    json.dump(data, json_file, ensure_ascii=False, indent=4)

# print(f"Data has been saved to {json_file_path}")

# Declare variables to store extracted data
album_list = []   # List to store album data for all items
artist_list = []  # List to store artist data for all items
song_list = []    # List to store song data for all items

# Extract album, artist, and song data
for item in data['items']:
    track = item.get("track", {})
    albums = track.get("album", {})
    artists = track.get("artists", [])

    # Extract album data
    album_data = {
        "album_id": albums['id'],
        "album_name": albums['name'],
        "release_date": albums['release_date'],
        "total_tracks": albums['total_tracks'],
        "external_urls": albums['external_urls']['spotify']
    }
    album_list.append(album_data)

    # Extract artist data
    for artist in artists:
        artist_data = {
            'artist_id': artist['id'],
            'artist_name': artist['name'],
            'external_url': artist['external_urls']['spotify']
        }
        artist_list.append(artist_data)

    # Extract song data
    song_data = {
        'song_id': track['id'],
        'song_name': track['name'],
        'song_duration_ms': track['duration_ms'],
        'song_url': track['external_urls']['spotify'],
        'song_popularity': track['popularity'],
        'added_at': item['added_at'],
        'album_id': albums['id'],
        'artist_id': artist_data['artist_id'],
        # 'artist_id': [artist['id'] for artist in artists]

    }
    song_list.append(song_data)

# Create DataFrames (df) from the lists
album_df = pd.DataFrame(album_list)
artist_df = pd.DataFrame(artist_list)
song_df = pd.DataFrame(song_list)

# transform release_date and added_date to datetime
album_df['release_date'] = pd.to_datetime(album_df['release_date'])
album_df.info()  # verify release_date is datetime
song_df['added_at'] = pd.to_datetime(song_df['added_at'])
song_df.info()  # verify added_date is datetime

