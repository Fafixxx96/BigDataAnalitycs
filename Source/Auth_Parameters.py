import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth

#FABIO CAPPARELLI DEVELOPPER CREDENTIAL
client_id = "4b7a6ff9e9e242208bcb12834b0244ac"
client_secret = "786b8540a1c74b3491db3f8f1170185d"

#PARAMETERS AND SCOPES FOR SPOTIFY QUERIES
redirect_uri = "http://localhost:8080"
scope = 'playlist-read-private'
scope2 = 'user-library-read'
scope3 = "playlist-modify-public"

#CLIENTS FOR SPOTIFY CONNECTION
client_1 = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id, 
                                                           client_secret=client_secret))

client_2 = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, 
                                                client_secret=client_secret, 
                                                redirect_uri=redirect_uri, 
                                                scope=scope))

client_3 = spotipy.Spotify(auth_manager=SpotifyOAuth( client_id=client_id, 
                                                      client_secret=client_secret, 
                                                      redirect_uri=redirect_uri, 
                                                      scope=scope2 ))

client_4 = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, 
                                                client_secret=client_secret, 
                                                redirect_uri=redirect_uri, 
                                                ))

client_5 = spotipy.Spotify(auth_manager=SpotifyOAuth( client_id=client_id, 
                                                      client_secret=client_secret, 
                                                      redirect_uri=redirect_uri, 
                                                      scope=scope3 ))