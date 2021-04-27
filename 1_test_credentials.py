import argparse
import logging
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

"""
Using my "Fabio Capparelli" user credentials for developpers.

follow sdk_procedures.md file
"""

#clientId and clientSecret for APP in spotify_sdk site.

client_id = "4b7a6ff9e9e242208bcb12834b0244ac"
client_secret = "786b8540a1c74b3491db3f8f1170185d"

logger = logging.getLogger('artist_albums')
logging.basicConfig(level='INFO')

auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(auth_manager=auth_manager)

def get_artist(name):
    results = sp.search(q='artist:' + name, type='artist')
    items = results['artists']['items']
    if len(items) > 0:
        return items[0]
    else:
        return None

def show_artist_albums(artist):
    albums = []
    print(artist['id'])
    results = sp.artist_albums(artist['id'], album_type='album')
    albums.extend(results['items'])
    while results['next']:
        results = sp.next(results)
        albums.extend(results['items'])
    seen = set()  # to avoid dups
    albums.sort(key=lambda album: album['name'].lower())
    for album in albums:
        name = album['name']
        if name not in seen:
            logger.info('ALBUM: %s', name)
            seen.add(name)

def show_artist_tracks(artist):
    results = sp.search(q=artist, limit=20)
    print(len(results))
    for i, t in enumerate(results['tracks']['items']):
        print(' ', i, t['name'])

def show_recommendations_for_artist(artist):
    results = sp.recommendations(seed_artists=[artist['id']])
    for track in results['tracks']:
        logger.info('Recommendation: %s - %s', track['name'],
                    track['artists'][0]['name'])


def main():
    
    #urn = 'spotify:artist:3jOstUTkEu2JkjvRdBA5Gu' #uniform resource name
    artist = get_artist('tiziano ferro')
    if artist:
        show_artist_albums(artist)
    else:
        logger.error("Can't find artist: %s", artist)
    


if __name__ == "__main__":
    main()
