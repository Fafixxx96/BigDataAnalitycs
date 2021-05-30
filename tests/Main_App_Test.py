import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
import json


#Fabio Capparelli credentials
client_id = "4b7a6ff9e9e242208bcb12834b0244ac"
client_secret = "786b8540a1c74b3491db3f8f1170185d"
redirect_uri = "http://localhost:8080"


sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))
scope = 'playlist-read-private'
sp1 = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, scope=scope))

def json_print(js):
  print(json.dumps(js, indent=4, sort_keys=True))

def print_artist(name):
  id = sp.search(q='artist:' + name, type='artist')
  json_print(id)

def get_artist_id(name):
  a_json = sp.search(q='artist:' + name, type='artist')
  items = a_json['artists']['items']
  if len(items) > 0:
    print(items[0]['id'])
    return items[0]['id']
  else:
    print("ERROR: Artist NotFound")
    return None

def show_album_tracks(album):
  tracks = []
  results = sp.album_tracks(album['id'])
  tracks.extend(results['items'])
  while results['next']:
    results = sp.next(results)
    tracks.extend(results['items'])
  for i, track in enumerate(tracks):
    print(i + 1, track['name'])

def show_artist_albums(artist_id):
  albums = []
  results = sp.artist_albums(artist_id, album_type='album')
  albums.extend(results['items'])
  while results['next']:
    results = sp.next(results)
    albums.extend(results['items'])
  seen = set()  # to avoid dups
  albums.sort(key=lambda album: album['name'].lower())
  for album in albums:
    name = album['name']
    if name not in seen:
      print("ALBUM: ", name)
      seen.add(name)
    show_album_tracks(album)

def show_user_playlist():
  results = sp1.current_user_playlists(limit=50)
  #json_print(results)
  for i, item in enumerate(results['items']):
    print("%d %s" % (i, item['id']))

def main():
  # urn = 'spotify:artist:3jOstUTkEu2JkjvRdBA5Gu' #uniform resource name
  #a = get_artist_id('Tiziano Ferro')
  #artist = print_artist('Tiziano Ferro')
  #a_id = get_artist_id("Fabri Fibra")
  #show_artist_albums(a_id)
  show_user_playlist()

if __name__ == "__main__":
  main()