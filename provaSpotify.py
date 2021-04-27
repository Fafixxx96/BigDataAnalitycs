import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
import json

"""

A python script for collecting data regarding audio features of tracks belonging to some Spotify user's playlists

"""

"""
Define the credentials
"""

client_id = "4b7a6ff9e9e242208bcb12834b0244ac"
client_secret = "786b8540a1c74b3491db3f8f1170185d"
redirect_uri = "http://localhost:8080"
scope = "playlist-read-private"

"""
Creation of the Spotify Client
"""

client = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                                   client_secret=client_secret,
                                                   redirect_uri=redirect_uri,
                                                   scope=scope))


"""
Returns an array containing the IDs of all the playlists belonging to a given Spotify User
"""

def get_playlists_id(user_id):
    playlist_list = []
    results = client.user_playlists(user_id)
    playlist_list.extend(results['items'])
    while results['next']:
        results = client.next(results)
        playlist_list.extend(results['items'])
    id_list = []
    for playlist in playlist_list:
        id_list.append(playlist['id'])
    return id_list


"""
Returns the [ID, Name, Duration in ms, Explicitness, Popularity]  of all the tracks belonging to a given Playlist 
"""

def get_playlist_tracks_general_info(playlist_id):
    tracks = []
    results = client.playlist_items(playlist_id=playlist_id)
    tracks.extend(results['items'])
    while results['next']:
        results = client.next(results)
        tracks.extend(results['items'])
    info = []
    for item in tracks:
        track_obj = item['track']
        features = [track_obj['id'],
                    track_obj['name'],
                    track_obj['duration_ms'],
                    track_obj['explicit'],
                    track_obj['popularity']]
        info.append(features)

    return info
    #for i, track in enumerate(info):
        #print(track)


"""
Returns a dataset containing the general information about some tracks, header included, 
ready to be transformed into a Dataframe
"""

def get_general_info_dataset(playlists_id):
    dataset = [['ID','Name','Duration_ms','Explicitness','Popularity']]
    for id in playlists_id:
        current_playlist_tracks = get_playlist_tracks_general_info(id)
        for track in current_playlist_tracks:
            dataset.append(track)
    return dataset
    #for row in dataset:
       # print(row)



"""
Returns a dataset containing the ID and the audio features about some tracks, header included, 
ready to be transformed into a Dataframe
"""

def get_tracks_audio_features_dataset(track_ids):
    dataset = [['ID',
                'danceability',
                'energy',
                'key',
                'loudness',
                'mode',
                'speechiness',
                'acousticness',
                'instrumentalness',
                'liveness',
                'valence',
                'tempo',
                'type',
                'id',
                'uri',
                'track_href',
                'analysis_url',
                'duration_ms',
                'time_signature']]
    for current_id in track_ids:
        track_features = client.audio_features(current_id)[0]
        new_features = [current_id]
        for i in range(1, len(dataset[0])):
            new_features.append(track_features[dataset[0][i]])
        dataset.append(new_features)
    for row in dataset:
        print(row)
    return dataset

def main():
    lista = get_playlists_id('prp468n1n5qp2sdr1ps5hk8t0')
    general_dataset = get_general_info_dataset(lista)
    tracks_ids = []
    for i in range(1,len(general_dataset)):
        tracks_ids.append(general_dataset[i][0])
    get_tracks_audio_features_dataset(tracks_ids)

if __name__ == "__main__":
    main()


