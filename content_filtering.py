import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
import json


#Fabio Capparelli credentials
client_id = "4b7a6ff9e9e242208bcb12834b0244ac"
client_secret = "786b8540a1c74b3491db3f8f1170185d"
redirect_uri = "http://localhost:8080"
scope = 'playlist-read-private'
scope2 = 'user-library-read'
scope3 = "playlist-modify-public"

fabio_capparelli_id = "11102339711"
francesco_raco_id = "prp468n1n5qp2sdr1ps5hk8t0"
pierpaolo_presta_id = "1198192219"

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

def json_print(js):
  print(json.dumps(js, indent=4, sort_keys=True))

user_tracks_set = { 'id': [], "name": [], "artist": []}
new_releases_set = { 'id': [],  "name": [], "artist": []}

def add_tracks_set(track_id, track_name, track_artist):
    global user_tracks_set
    if not (track_id in user_tracks_set['id']):
        user_tracks_set['id'].append(track_id)
        user_tracks_set['name'].append(track_name)
        user_tracks_set['artist'].append(track_artist)

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
def get_user_paylists(user_id):
    playlist_list = []
    results = client_2.user_playlists(user_id)
    playlist_list.extend(results['items'])
    while results['next']:
        results = client_2.next(results)
        playlist_list.extend(results['items'])
    return playlist_list

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
            s = ""
            for artist in artists:
                s += " " + artist['name']
            add_tracks_set(track_obj['id'], track_obj['name'], s)

def new_spotify_releases():
    response = client_2.new_releases()
    while response:
        albums = response['albums']
        for album in albums['items']:
            tracks_album = client_3.album_tracks(album['id'])
            for track in tracks_album['items']:
                add_new_releases_set(track['id'], track['name'], album['name'])
        if albums['next']:
            response = client_2.next(albums)
        else:
            response = None

def return_value(inf, sup, value):
        int1 = value - inf
        int2 = sup - value
        if(int1 <= int2):
            return inf*5
        else:
            return sup*5

def convert_attribute(attribute):
    if(attribute <= 0.2):
        return return_value(0.0, 0.2, attribute)
    elif(attribute > 0.20 and attribute <= 0.4 ):
        return return_value(0.2, 0.4, attribute)
    elif(attribute > 0.4 and attribute <= 0.6 ):
        return return_value(0.4, 0.6, attribute)
    elif(attribute > 0.6 and attribute <= 0.8 ):
      return return_value(0.6, 0.8, attribute)
    elif(attribute > 0.8 and attribute <= 1 ):
      return return_value(0.8, 1.0, attribute)
    return 0

def convert_attribute2(attribute):
   return return_value(0, 1, attribute)
           
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
    j = 0
    for current_id in tracks_set['id']:
        track_features = client_2.audio_features(current_id)[0]
        if track_features is not None:
            new_features = [current_id, tracks_set['name'][j], tracks_set['artist'][j]]
            j+=1
            for i in range(3, len(dataset[0])):
                new_features.append(track_features[dataset[0][i]])
            dataset.append(new_features)
    dataset2 = []
    for row in dataset:
        if not(row == dataset[0]):
            dataset2.append(preprocessing_track_features(row))
    return dataset2
    

def preprocessing_track_features(track_features):
    new_row = []
    new_row.append(track_features[0])
    new_row.append(track_features[1])
    new_row.append(track_features[2])
    new_row.append(convert_attribute(track_features[3]))# "Danceability"
    new_row.append(convert_attribute(track_features[4]))# "Energy"
    new_row.append(convert_attribute(track_features[5]))# "Mode"
    new_row.append(convert_attribute(track_features[6]))# "Speechiness"
    new_row.append(convert_attribute(track_features[7]))# "Acousticness"
    new_row.append(convert_attribute2(track_features[8]))# "Instrumentalness"
    new_row.append(convert_attribute(track_features[9]))# "Valence"
    return new_row

d = 0
e = 0
m = 0
s = 0
a = 0
i = 0
v = 0
length_dataset = 0

def mean_value_user_track_features(dataset):
    global d, e, m, s, a, i, v, length_dataset
    for row in dataset:
        if not(row == dataset[0]):
            d += row[3]
            e += row[4]
            m += row[5]
            s += row[6]
            a += row[7]
            i += row[8]
            v += row[9]
    length_dataset = len(dataset)-1
    record = []
    d = (d/length_dataset)
    record.append(round(d))
    e = (e/length_dataset)
    record.append(round(e))
    m = (m/length_dataset)
    record.append(round(m))
    s = (s/length_dataset)
    record.append(round(s))
    a = (a/length_dataset)
    record.append(round(a))
    i = (i/length_dataset)
    record.append(round(i))
    v = (v/length_dataset)
    record.append(round(v))
    #print(record)
    return record

def build_recommendation(user_record, new_tracks):
    recommedation = { 'id': [], 'name': [], 'artist': [], 'value': [] }
    i=0
    for row in new_tracks:
        sum = 0
        j=3
        for val in user_record:
            val2 = new_tracks[i][j]
            ris = val * val2
            sum = sum + ris
            j += 1
        
        if sum > 50:
            recommedation['id'].append(row[0])
            recommedation['name'].append(row[1])
            recommedation['artist'].append(row[2])
            recommedation['value'].append(sum)
        i += 1
    #print(sum)
    return(recommedation) 

def print_dict(diz):
    for i in range (0, len(diz['id'])):
       print(diz['name'][i], " | ", diz['artist'][i],  " | ", diz['value'][i])

def new_playlist(user_id, name):
    client_5.user_playlist_create(user_id, name)

def add_to_playlist(playlist_id, songs_ids):
    for id in songs_ids:
        client_5.playlist_add_items(playlist_id, id)

def print_playlists(playlists):
    for i, p in enumerate(playlists):
        print(i, p['id'], p['name'])

def main():
    print()
    user_id = input("Insert user id: ")
    print()
    while (user_id == None):
        print()
        user_id = input("Please insert user id: ")
    user_playlists = get_user_paylists(user_id)
    print_playlists(user_playlists)
    get_playlists_tracks(user_playlists)
   
    user_audio_features_dataset = get_tracks_audio_features_dataset(user_tracks_set)
    user_record = mean_value_user_track_features(user_audio_features_dataset)
    print(user_record)
    new_spotify_releases()
    new_audio_features_dataset = get_tracks_audio_features_dataset(new_releases_set)
    recommendations = build_recommendation(user_record, new_audio_features_dataset)
    print_dict(recommendations)
    print(recommendations['id'])

    new = input("Do you want to create a new playlist with these songs [y,n]?: ")
    print()
    if(new == 'y'):
        name = input("Insert playlist name: ")
        while(name == None):
            print()
            name = input("No void name allowed, please insert a playlist name: ")
        new_playlist(user_id, name)
        print_playlists(user_playlists)
        add_to_playlist(user_playlists[len(user_playlists)-1]['id'], recommendations['id'])

    elif(new == 'n'):
        name = input("Do you want to add these songs to an existing playlist [y,n]?: ")

if __name__ == "__main__":
  main()