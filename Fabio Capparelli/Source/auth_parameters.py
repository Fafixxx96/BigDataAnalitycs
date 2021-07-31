import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
from requests.exceptions import ReadTimeout

#FABIO CAPPARELLI DEVELOPPER CREDENTIAL
client_id = "4b7a6ff9e9e242208bcb12834b0244ac"
client_secret = "1240a182d6324f2a97d233e227d1ed75"

#PARAMETERS AND SCOPES FOR SPOTIFY QUERIES
redirect_uri = "http://localhost:8085"
scope = 'playlist-read-private'
scope2 = 'user-library-read'
scope3 = "playlist-modify-public"

#CLIENTS FOR SPOTIFY CONNECTION
client_1 = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id, 
                                                           client_secret=client_secret), requests_timeout=20, retries=10)

client_2 = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, 
                                                client_secret=client_secret, 
                                                redirect_uri=redirect_uri, 
                                                scope=scope), requests_timeout=20, retries=10)

client_3 = spotipy.Spotify(auth_manager=SpotifyOAuth( client_id=client_id, 
                                                      client_secret=client_secret, 
                                                      redirect_uri=redirect_uri, 
                                                      scope=scope2 ),requests_timeout=20, retries=10)

client_4 = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, 
                                                client_secret=client_secret, 
                                                redirect_uri=redirect_uri),requests_timeout=20, retries=10)

client_5 = spotipy.Spotify(auth_manager=SpotifyOAuth( client_id=client_id, 
                                                      client_secret=client_secret, 
                                                      redirect_uri=redirect_uri, 
                                                      scope=scope3 ), requests_timeout=20, retries=10)