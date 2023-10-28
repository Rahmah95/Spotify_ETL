import API_config
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import json
import pandas as pd

# Set the Spotify API client credentials
CLIENT_ID = API_config.client_id
CLIENT_SECRET = API_config.client_secret


# Function to fetch playlist data from Spotify
def fetch_playlist_data(playlist_link):
    """ To fetch playlist data from Spotify """
    # Initialize a Spotify client
    client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    # Extract the playlist URI from the provided link
    playlist_URI = playlist_link.split("/")[-1].split("?")[0]
    # Use the Spotify client to fetch data for the playlist
    data = sp.playlist_items(playlist_URI)
    return data


# Function to save data to a JSON file
def save_data_to_json(data, json_file_path):
    """ To save raw data to a JSON file """
    with open(json_file_path, 'w', encoding='utf-8') as json_file:
        # Write the playlist data to the JSON file with formatting
        json.dump(data, json_file, ensure_ascii=False, indent=4)


# Function to extract album data
def extract_album(album):
    """ To extract album data """
    album_data = {
        "album_id": album['id'],
        "album_name": album['name'],
        "release_date": album['release_date'],
        "total_tracks": album['total_tracks'],
        "external_urls": album['external_urls']['spotify']
    }
    return album_data


# Function to extract artist data
def extract_artist(artist):
    """ To extract artist data """
    artist_data = {
        'artist_id': artist['id'],
        'artist_name': artist['name'],
        'external_url': artist['external_urls']['spotify']
    }
    return artist_data


# Function to extract song data
def extract_song_data(data):
    """ To extract song data """
    song_data_list = []
    for item in data['items']:
        track = item.get("track", {})
        albums = track.get("album", {})
        artists = track.get("artists", [])

        for artist in artists:
            artist_data = extract_artist(artist)

            song_data = {
                'song_id': track['id'],
                'song_name': track['name'],
                'song_duration_ms': track['duration_ms'],
                'song_url': track['external_urls']['spotify'],
                'song_popularity': track['popularity'],
                'added_at': item['added_at'],
                'album_id': albums['id'],
                'artist_id': artist_data['artist_id']
            }
            song_data_list.append(song_data)

    return song_data_list


# Function to validate and clean dataframes
def validate_dataframes(song_df, album_df, artist_df):
    """ To validate and clean dataframes """
    # Remove duplicate rows based on 'song_id', 'album_id', and 'artist_id' columns
    song_df.drop_duplicates(subset='song_id', inplace=True)
    album_df.drop_duplicates(subset='album_id', inplace=True)
    artist_df.drop_duplicates(subset='artist_id', inplace=True)

    # Remove rows with any null values in the DataFrames
    song_df.dropna(how='any', inplace=True)
    album_df.dropna(how='any', inplace=True)
    artist_df.dropna(how='any', inplace=True)


# Function to change date columns to datetime format
def transform_dateframes(song_df, album_df, artist_df):
    """ To transform date in DataFrames """
    song_df['added_at'] = pd.to_datetime(song_df['added_at'])
    album_df['release_date'] = pd.to_datetime(album_df['release_date'])


# Function to create and save Excel files for each DataFrame
def export_dataframes(song_df, album_df, artist_df):
    """ To  create and save dataframes into Excel files """
    # remove datetime -> timezone information to match excel time format
    song_df['added_at'] = song_df['added_at'].dt.tz_localize(None)
    album_df['release_date'] = album_df['release_date'].dt.tz_localize(None)

    song_df.to_excel("files/song_data.xlsx", index=False)
    album_df.to_excel("files/album_data.xlsx", index=False)
    artist_df.to_excel("files/artist_data.xlsx", index=False)


# Main function to fetch and process playlist data
def main(playlist_link, json_file_path):
    """ To put all functions to work together """
    # Fetch data from the Spotify playlist
    data = fetch_playlist_data(playlist_link)
    # Save the fetched data to a JSON file
    save_data_to_json(data, json_file_path)

    # Extract and process song, album, and artist data
    song_data_list = extract_song_data(data)
    album_data = [extract_album(item['track']['album']) for item in data['items']]
    artist_data = [extract_artist(artist) for item in data['items'] for artist in item['track']['artists']]

    # Convert the processed data into Pandas DataFrames
    song_df = pd.DataFrame(song_data_list)
    album_df = pd.DataFrame(album_data)
    artist_df = pd.DataFrame(artist_data)

    # Validate and clean dataframes
    validate_dataframes(song_df, album_df, artist_df)

    # Transform data
    transform_dateframes(song_df, album_df, artist_df)

    # Save data to Excel files
    export_dataframes(song_df, album_df, artist_df)

    return song_df, album_df, artist_df


# Check if the script is run as the main program
if __name__ == '__main__':
    # Specify the Spotify playlist link and the JSON file path
    playlist_link = "https://open.spotify.com/playlist/37i9dQZEVXbNG2KDcFcKOF?si=3ba7f1262cdb41aa"
    json_file_path = "spotify_data.json"

    # Call the main function with the JSON file path as a arguments
    # song_df = main(playlist_link, json_file_path)[0]
    # album_df = main(playlist_link, json_file_path)[1]
    # artist_df = main(playlist_link, json_file_path)[2]

    # tuples unpacking for multiple return values
    song_df, album_df, artist_df = main(playlist_link, json_file_path)
    print(song_df)
    # song_df, album_df, artist_df = main(playlist_link, json_file_path)
