import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
import json
from apyori import apriori
import pandas as pd
import numpy as np

#Fabio Capparelli credentials
client_id = "4b7a6ff9e9e242208bcb12834b0244ac"
client_secret = "786b8540a1c74b3491db3f8f1170185d"
redirect_uri = "http://localhost:8080"
scope = 'playlist-read-private'
fabio_capparelli_id = "11102339711"
francesco_raco_id = "prp468n1n5qp2sdr1ps5hk8t0"

client_1 = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id, 
                                                           client_secret=client_secret))

client = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, 
                                                client_secret=client_secret, 
                                                redirect_uri=redirect_uri, 
                                                scope=scope))

def json_print(js):
  print(json.dumps(js, indent=4, sort_keys=True))


def get_playlists(user_id):
    playlist_list = []
    results = client.user_playlists(user_id)
    playlist_list.extend(results['items'])
    while results['next']:
        results = client.next(results)
        playlist_list.extend(results['items'])
    list_play = []
    for playlist in playlist_list:
        list_play.append([playlist['id'], playlist['name']])
    return list_play

def get_tracks_in_playlist(playlist_id):
    tracks = []
    results = client.playlist_items(playlist_id=playlist_id)
    tracks.extend(results['items'])
    while results['next']:
        results = client.next(results)
        tracks.extend(results['items'])
    info = []
    for item in tracks:
        track_obj = item['track']
        features = track_obj['id']
        info.append(features)
    return info

def get_tracks_audio_features_dataset(track_ids):
    dataset = [['ID',
                'danceability',
                'energy',
                'mode',
                'speechiness',
                'acousticness',
                'instrumentalness',
                'valence']]
    for current_id in track_ids:
        track_features = client.audio_features(current_id)[0]
        new_features = [current_id]
        for i in range(1, len(dataset[0])):
            new_features.append(track_features[dataset[0][i]])
        dataset.append(new_features)
    dataset2 = []
    for row in dataset:
        if not(row == dataset[0]):
            dataset2.append(preprocessing_track_features(row))
    return dataset2

def convert_attribute(attribute, name):
    if(attribute < 0.33):
        return  name + "_LOW"
    elif(attribute > 0.66):
        return  name + "_HIGH"
    else:
        return  name + "_MEDIUM"

def convert_attribute2(attribute, name):
    if(attribute < 0.5):
        return  name + "_LOW"
    else:
        return  name + "_HIGH"

def preprocessing_track_features(track_features):
    new_row = []
    new_row.append(track_features[0])
    new_row.append(convert_attribute(track_features[1], "Danceability"))
    new_row.append(convert_attribute(track_features[2], "Energy"))
    new_row.append(convert_attribute(track_features[3], "Mode"))
    new_row.append(convert_attribute(track_features[4], "Speechiness"))
    new_row.append(convert_attribute(track_features[5], "Acousticness"))
    new_row.append(convert_attribute2(track_features[6], "Instrumentalness"))
    new_row.append(convert_attribute(track_features[7], "Valence"))
    #print(new_row)
    return new_row

def association_rules(records):
    apriori_alg = apriori(records, min_support=0.40, min_confidence=0.7, min_lift=1.2, min_length=2) 
    results = list(apriori_alg)
    return results

def print_rules(association_rules):
    for item in association_rules:
        # first index of the inner list
        # Contains base item and add item
        pair = item[0] 
        items = [x for x in pair]
        print()
        print("Rule: " + items[0] + " -> " + items[1] + " " + items[2] )
        #second index of the inner list
        print("Support: " + str(item[1]))
        #third index of the list located at 0th
        #of the third index of the inner list
        print("Confidence: " + str(item[2][0][2]))
        print("Lift: " + str(item[2][0][3]))
        print("=====================================")

def main():
    # urn = 'spotify:artist:3jOstUTkEu2JkjvRdBA5Gu' #uniform resource name
    #a = get_artist_id('Tiziano Ferro')
    #artist = print_artist('Tiziano Ferro')
    #a_id = get_artist_id("Fabri Fibra")
    #show_artist_albums(a_id)
    playlists = get_playlists(fabio_capparelli_id)
    for p in playlists:
        print("PLAYLIST:", p[1])
        songs = get_tracks_in_playlist(p[0])
        dataset = get_tracks_audio_features_dataset(songs)
        rules_mined = association_rules(dataset)
        print_rules(rules_mined)
        break      
    

if __name__ == "__main__":
  main()