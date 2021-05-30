import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
import json
from auth_parameters import *

#------------------------------------------GLOBAL VARIABLES------------------------------------------#

#FABIO CAPPARELLI DEVELOPPER CREDENTIAL
#client_id = "4b7a6ff9e9e242208bcb12834b0244ac"
#client_secret = "786b8540a1c74b3491db3f8f1170185d"

#PARAMETERS AND SCOPES FOR SPOTIFY QUERIES
redirect_uri = "http://localhost:8080"
scope = 'playlist-read-private'
scope2 = 'user-library-read'
scope3 = "playlist-modify-public"

#SPOTIFY USER IDS
fabio_capparelli_id = "11102339711"
francesco_raco_id = "prp468n1n5qp2sdr1ps5hk8t0"
pierpaolo_presta_id = "1198192219"

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

#DICT/SETS USED FOR STORING USER PLAYLIST TRACKS AND NEW SPOTIFY RELEASES
user_tracks_set = { 'id': [], "name": [], "artist": []}
new_releases_set = { 'id': [],  "name": [], "artist": []}

#------------------------------------------GLOBAL FUNCTIONS------------------------------------------#

#FUNCTION USED TO PRINT THE RETURNED JSON RESULTS FROM QUERIES
def json_print(js):
  print(json.dumps(js, indent=4, sort_keys=True))

#FUNCTION USED TO PRINT RECOMENDATION DICT
def print_dict(diz):
    for i in range (0, len(diz['id'])):
       print(diz['name'][i], " | ", diz['artist'][i],  " | ", diz['value'][i])

#FUNCITON USED TO PRINT USER PLAYLISTS
def print_playlists(playlists):
    for i, p in enumerate(playlists):
        print(i, p['id'], p['name'])

#FUNCTION USED TO ADD USER TRACKS TO THE OWN DICT/SET
def add_tracks_set(track_id, track_name, track_artist):
    global user_tracks_set
    if not (track_id in user_tracks_set['id']):
        user_tracks_set['id'].append(track_id)
        user_tracks_set['name'].append(track_name)
        user_tracks_set['artist'].append(track_artist)

#FUNCTION USED TO ADD NEW RELEASE TRACKS TO THE OWN DICT/SET
def add_new_releases_set(track_id, track_name, track_artist):
    global new_releases_set
    if not (track_id in new_releases_set['id']):
        new_releases_set['id'].append(track_id)
        new_releases_set['name'].append(track_name)
        new_releases_set['artist'].append(track_artist)

"""        
def print_tracks_set():
    for i in range (0, len(user_tracks_set['id'])):
        print(i, user_tracks_set['id'][i], user_tracks_set['name'][i]) 
   
def user_tracks_in_saved_tracks():
    results = client_3.current_user_saved_tracks()
    for item in results['items']:
        track = item['track']
        add_tracks_set(track['id'], track['name'])
        
def user_tracks_saved_albums():
    albums = client_3.current_user_saved_albums()
    for item in albums['items']:
        album = item['album']
        tracks_album = client_3.album_tracks(album['id'])
        for track in tracks_album['items']:
            add_tracks_set(track['id'], track['name'])

def user_tracks_in_playlists(user_id):
    playlists = client_2.user_playlists(user_id)
    for item in playlists['items']:
        results = client_2.playlist_items(playlist_id=item['id'])
        for item in results['items']:
            track = item['track']
            add_tracks_set(track['id'], track['name'])
"""
#FUNCTION USED TO RETRIEVE USER PLAYLISTS
def get_user_paylists(user_id):
    playlist_list = []
    results = client_2.user_playlists(user_id)
    playlist_list.extend(results['items'])
    while results['next']:
        results = client_2.next(results)
        playlist_list.extend(results['items'])
    return playlist_list

#FUNCTION USED TO RETRIEVE TRACKS IN USER PLAYLISTS
def get_playlists_tracks(playlist_list):
    for playlist in playlist_list:
        tracks = []
        results = client_2.playlist_items(playlist_id=playlist['id'])
        tracks.extend(results['items'])
        while results['next']:
            results = client_2.next(results)
            tracks.extend(results['items'])
        for item in tracks:
            track_obj = item['track']
            artists = track_obj['artists']
            artists_names = ""
            for artist in artists:
                artists_names += (" " + artist['name'])
            add_tracks_set(track_obj['id'], track_obj['name'], artists_names)

#FUNCTION USED TO DISCOVER NEW RELEASE AND ADD IT IN THE OWN SET
def new_spotify_releases():
    response = client_2.new_releases()
    while response:
        albums = response['albums']
        for album in albums['items']:
            tracks_album = client_3.album_tracks(album['id'])
            artists = album['artists']
            artists_names = ""
            for artist in artists:
                artists_names += (" " + artist['name'])
            for track in tracks_album['items']:
                add_new_releases_set(track['id'], track['name'], artists_names)          
        if albums['next']:
            response = client_2.next(albums)
        else:
            response = None

#FUNCTION USED TO CONVERT ATTRIBUTE IN A VALUE IN THE INTEGER INTERVAL [0, 5]
def convert_attribute(attribute):
  return round(attribute*5)

#FUNCTION USED TO RETRIEVE THE AUDIO FEATURE FOR THE TRACKS IN THE SET         
def get_tracks_audio_features_dataset(tracks_set):
    dataset = [['ID',
                'NAME',
                'ARTIST',
                'danceability',
                'energy',
                'mode',
                'speechiness',
                'acousticness',
                'instrumentalness',
                'valence']]
    for j, current_id in enumerate(tracks_set['id']):
        track_features = client_2.audio_features(current_id)[0]
        if track_features is not None:
            new_features = [current_id, tracks_set['name'][j], tracks_set['artist'][j]]
            for i in range(3, len(dataset[0])):
                new_features.append(track_features[dataset[0][i]])
            dataset.append(new_features)
    dataset2 = []
    for row in dataset:
        if not(row == dataset[0]):
            dataset2.append(preprocessing_track_features(row))
    return dataset2

#FUCTION USED TO PRE-PROCESS THE VALUE OF AUDIO_FEATURES
def preprocessing_track_features(track_features):
    new_row = []
    for i, feature in enumerate(track_features):
        if(i<3):
            new_row.append(feature)
        else:
            new_row.append(convert_attribute(feature))
    return new_row

#FUCTION USED TO GET THE USER AUDIO FEATURES VALUES, IT IS USED THE AVERAGE VALUE FOR EACH AUDIO FEATURE
def mean_value_user_track_features(dataset):
    len_dataset = len(dataset)-1
    vect = [0, 0, 0, 0, 0, 0, 0]
    for row in dataset:
        if not(row == dataset[0]):
            for i in range (0, len(vect)):
                vect[i] += row[i+3]
    for i in range (0, len(vect)):
        vect[i] = round(vect[i]/len_dataset)
    return vect

#FUCTION USED TO BUIL RECOMMENDATION DICT, IT SUGGEST NEW TRACKS.
def build_recommendation(user_record, new_tracks):
    recommendation = { 'id': [], 'name': [], 'artist': [], 'value': [] }
    sum_of_sums = 0
    for row in new_tracks:
        sum = 0
        for j, val in enumerate(user_record):
            sum += val*row[j+3]
        if sum > 50:
            recommendation['id'].append(row[0])
            recommendation['name'].append(row[1])
            recommendation['artist'].append(row[2])
            recommendation['value'].append(sum)
        sum_of_sums += sum
    print(sum_of_sums/len(new_tracks))
    return(recommendation) 

#FUCTION USED TO CREATE A NEW PLAYLIST
def new_playlist(user_id, name):
    client_5.user_playlist_create(user_id, name)

#FUCTION USED TO ADD TRACKS TO A PLAYLIST
def add_tracks_to_playlist(playlist_id, songs_ids):
    for id in songs_ids:
        client_5.playlist_add_items(playlist_id, id)

def main():
    
    print()
    user_id = input("Insert user id: ")
    print()
    while (user_id == None):
        print()
        user_id = input("Please insert non-empty user id: ")
    
    user_playlists = get_user_paylists(user_id)
    #print_playlists(user_playlists)
    get_playlists_tracks(user_playlists)
   
    user_audio_features_dataset = get_tracks_audio_features_dataset(user_tracks_set)
    user_record = mean_value_user_track_features(user_audio_features_dataset)
    print(user_record)

    new_spotify_releases()
    new_audio_features_dataset = get_tracks_audio_features_dataset(new_releases_set)
    recommendations = build_recommendation(user_record, new_audio_features_dataset)
    print_dict(recommendations)
    

    """
    new = input("Do you want to create a new playlist with these songs [y,n]?: ")
    print()
    if(new == 'y'):
        name = input("Insert playlist name: ")
        while(name == None):
            print()
            name = input("No void name allowed, please insert a playlist name: ")
        new_playlist(user_id, name)
        print_playlists(user_playlists)
        add_tracks_to_playlist(user_playlists[len(user_playlists)-1]['id'], recommendations['id'])

    elif(new == 'n'):
        name = input("Do you want to add these songs to an existing playlist [y,n]?: ")
    """

if __name__ == "__main__":
  main()
