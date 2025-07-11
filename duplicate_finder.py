import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import re 
import os
from dotenv import load_dotenv

load_dotenv()

# Spotify API Client Config
CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')

if not CLIENT_ID or not CLIENT_SECRET:
    raise EnvironmentError(
        "Missing Spotify credentials. "
        "Set SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET in a .env file or environment variables."
    )


def extract_playlist_id(playlist_url):
    """
    Extracts playlist ID from a Spotify playlist URL.
    """
    match = re.search(r'playlist/([a-zA-Z0-9]+)', playlist_url)
    if match:
        return match.group(1)
    else:
        raise ValueError("Invalid Spotify playlist URL.")


def get_playlist_tracks(playlist_url):
    """
    Given a Spotify playlist URL, returns a list of (song title, artist) tuples.
    """
    playlist_id = extract_playlist_id(playlist_url)
    
    # Authenticate with Spotify
    auth_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
    sp = spotipy.Spotify(auth_manager=auth_manager)
    
    # Fetch playlist tracks
    results = sp.playlist_items(playlist_id, additional_types=['track'])
    tracks = []

    while results:
        for item in results['items']:
            track = item['track']
            if track:  # Skip if track is None (sometimes happens)
                title = track['name']
                artists = ', '.join(artist['name'] for artist in track['artists'])
                tracks.append((title, artists))
        # Pagination (in case playlist has >100 tracks)
        if results['next']:
            results = sp.next(results)
        else:
            results = None

    return tracks


def find_duplicates(tracks):
    """
    Given a list of (song title, artist) tuples, returns a list of (song title, artist) tuples of duplicated songs.
    """
    track_count = {}
    duplicates = []

    for title, artist in tracks:
        key = (title.lower(), artist.lower())

        if key in track_count:
            track_count[key] += 1
            if track_count[key] == 2:
                duplicates.append((title, artist))
        else:
            track_count[key] = 1
    
    return duplicates


def main():
    playlist_url = input("Enter Spotify playlist URL: ").strip()
    try:
        tracks = get_playlist_tracks(playlist_url)
        duplicates = find_duplicates(tracks)

        # Terminal Output
        if duplicates:
            print("\n Duplicate Tracks:")
            for track in duplicates:
                print(track[0],'-', track[1])
            print(f"\n Total duplicate tracks: {len(duplicates)}")
        else:
            print("\n No duplicate tracks found!")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
