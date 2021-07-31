import json
from auth_parameters import *



#------------------------------------------GLOBAL VARIABLES------------------------------------------#

#SPOTIFY USER IDS
fabio_capparelli_id = "11102339711"
francesco_raco_id = "prp468n1n5qp2sdr1ps5hk8t0"
pierpaolo_presta_id = "1198192219"

#DICT/SETS USED FOR STORING USER PLAYLIST TRACKS AND NEW SPOTIFY RELEASES
user_tracks_set = { 'id': [], "name": [], "artist": [], "link": [] }
new_releases_set = { 'id': [],  "name": [], "artist": [], "link": [] }

#------------------------------------------GLOBAL FUNCTIONS------------------------------------------#

#FUNCTION USED TO PRINT THE RETURNED JSON RESULTS FROM QUERIES
def json_print(js):
  print(json.dumps(js, indent=4, sort_keys=True))

#FUNCTION USED TO PRINT RECOMMENDATION DICT
def print_dict(diz):
    print('\n' + "> Recommented songs: " + '\n')
    for i, ids in enumerate (diz['id']):
        print('Song: ' + diz['name'][i])
        print('Artist: ' + diz['artist'][i])
        print('Recommendation Support: ' + str(float(diz['value'][i]/200))) 
        print('Reference Link: ' + diz['link'][i] + '\n') 

#FUNCITON USED TO PRINT USER PLAYLISTS
def print_playlists(playlists):
    for i, p in enumerate(playlists):
        print(i, p['id'], p['name'])

#FUNCTION USED TO ADD USER TRACKS TO THE OWN DICT/SET
def add_tracks_set(track_id, track_name, track_artist, track_link):
    global user_tracks_set
    if not (track_id in user_tracks_set['id']):
        user_tracks_set['id'].append(track_id)
        user_tracks_set['name'].append(track_name)
        user_tracks_set['artist'].append(track_artist)
        user_tracks_set['link'].append(track_link)

#FUNCTION USED TO ADD NEW RELEASE TRACKS TO THE OWN DICT/SET
def add_new_releases_set(track_id, track_name, track_artist, track_link):
    global new_releases_set
    if not (track_id in new_releases_set['id']):
        new_releases_set['id'].append(track_id)
        new_releases_set['name'].append(track_name)
        new_releases_set['artist'].append(track_artist)
        new_releases_set['link'].append(track_link)

#FUNCTION USED TO RETRIEVE USER PLAYLISTS
def search_user(user_id):
    try:
        user = client_2.user(user_id)
        #json_print(user)
        return user['display_name']
    except:
        print('Invalid User_Id!')
        return None

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
            url = track_obj['external_urls']
            if(len(url) > 0):
                add_tracks_set(track_obj['id'], track_obj['name'], artists_names, url['spotify'])

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
                url = track['external_urls']
                add_new_releases_set(track['id'], track['name'], artists_names, url['spotify'])       
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
                'LINK',
                'danceability',
                'energy',
                'liveness',
                'speechiness',
                'acousticness',
                'instrumentalness',
                'tempo',
                'valence']]
    for j, current_id in enumerate(tracks_set['id']):
        track_features = client_2.audio_features(current_id)[0]
        #json_print(track_features)
        if track_features is not None:
            new_features = [current_id, tracks_set['name'][j], tracks_set['artist'][j], tracks_set['link'][j]]
            for i in range(4, len(dataset[0])):
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
        if(i<4):
            new_row.append(feature)
        else:
            if( feature > 1):
               f = float(feature / 190) #for tempo
               new_row.append(convert_attribute(f))
            else:
               new_row.append(convert_attribute(feature))
    return new_row

#FUCTION USED TO GET THE USER AUDIO FEATURES VALUES, IT IS USED THE AVERAGE VALUE FOR EACH AUDIO FEATURE
def mean_value_user_track_features(dataset):
    len_dataset = len(dataset)-1
    vect = [0, 0, 0, 0, 0, 0, 0, 0]
    for row in dataset:
        if not(row == dataset[0]):
            for i in range(0, len(vect)):
                vect[i] += row[i+4]
    for i in range(0, len(vect)):
        vect[i] = round(vect[i]/len_dataset)
    return vect

#FUCTION USED TO BUIL RECOMMENDATION DICT, IT SUGGEST NEW TRACKS.
MAX_RATING = 200
def build_recommendation(user_record, new_tracks, support):
    recommendation = { 'id': [], 'name': [], 'artist': [], 'value': [], 'link': []}
    for row in new_tracks:
        sum = 0
        for j, val in enumerate(user_record):
            sum += val*row[j+4]
        if( float(sum) > float(support*MAX_RATING)):
            recommendation['id'].append(row[0])
            recommendation['name'].append(row[1])
            recommendation['artist'].append(row[2])
            recommendation['value'].append(sum)
            recommendation['link'].append(row[3])
    return recommendation 

#FUCTION USED TO CREATE A NEW PLAYLIST
def new_playlist(user_id, name):
    client_5.user_playlist_create(user_id, name)

#FUCTION USED TO ADD TRACKS TO A PLAYLIST
def add_tracks_to_playlist(playlist_id, songs_ids):
    for id in songs_ids:
        client_5.playlist_add_items(playlist_id, id)

def main():
    user_id = input('\n' + "> Please insert a user id: " + '\n')
    user = search_user(user_id)
    while (user == None):
        user_id = input('\n' + "> Please insert a correct user id: " + '\n')
        user = search_user(user_id)
    print('\n' + "> Building a recommendation system for: " + '\n' + user + '\n')

    user_playlists = get_user_paylists(user_id)
    get_playlists_tracks(user_playlists)
    
    user_audio_features_dataset = get_tracks_audio_features_dataset(user_tracks_set)
    user_record = mean_value_user_track_features(user_audio_features_dataset)
    print("> USER_PROFILE:")
    print('danceability', str(user_record[0]), 'energy', str(user_record[1]), 'liveness', str(user_record[2]), 'speechiness', str(user_record[3]),
          'acousticness', str(user_record[4]), 'instrumentalness', str(user_record[5]), 'tempo', str(user_record[6]), 'valence', str(user_record[7]))

    print('\n' + "> Looking for new releases . . .")
    new_spotify_releases()
    new_audio_features_dataset = get_tracks_audio_features_dataset(new_releases_set)

    support = input('\n' + "> Please insert support in range [0, 1]: " + '\n')
    while (float(support) > 1.0 and float(support) < 0.0):
        support = input('\n' + "> Please insert support in range [0, 1]: " + '\n')

    recommendations = build_recommendation(user_record, new_audio_features_dataset, float(support))
    while( len(recommendations['id']) == 0 ):
        print('\n' + "> No songs recommented, please try to put a lower support.")
        support_2 = input("> Please insert support in range [0, " +  support + "): " + '\n')
        while (float(support_2) >= float(support) and float(support_2) < 0.0):
            support_2 = input('\n' +"> Please insert support in range [0, " +  support+ "): " + '\n')
        recommendations = build_recommendation(user_record, new_audio_features_dataset, float(support_2))
        support = support_2
    print_dict(recommendations)
    
if __name__ == "__main__":
  main()