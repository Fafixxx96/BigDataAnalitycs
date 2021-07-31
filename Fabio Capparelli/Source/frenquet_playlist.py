from auth_parameters import *
import json
from apyori import apriori

#SPOTIFY USER IDS
fabio_capparelli_id = "11102339711"
francesco_raco_id = "prp468n1n5qp2sdr1ps5hk8t0"
pierpaolo_presta_id = "1198192219"

def json_print(js):
  print(json.dumps(js, indent=4, sort_keys=True))

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
def get_playlist_artists(playlist_id):
    tracks = []
    results = client_2.playlist_items(playlist_id=playlist_id)
    tracks.extend(results['items'])
    artists_names = []
    while results['next']:
          results = client_2.next(results)
          tracks.extend(results['items'])
    for item in tracks:
         track_obj = item['track']
         artists = track_obj['artists']
         
         for artist in artists:
             if(artist['name'] not in artists_names):
                 artists_names.append(artist['name']) 
    return artists_names    

def association_rules(records):
    apriori_alg = apriori(records, min_support=0.13, min_confidence=0.7, min_lift=1.2, min_length=3) 
    results = list(apriori_alg) 
    return results

def print_rules(association_rules):
    for item in association_rules:
        # first index of the inner list
        # Contains base item and add item
        pair = item[0] 
        items = [x for x in pair]
        
        s = "Rule: " + items[0] + " -> "
        for i in range (1,len(items)):
            if(i == len(items)-1):
                s += items[i]
                break
            s += items[i] + ", "
        print (s)
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
    artists_in_playlist = []
    playlists = get_user_paylists(pierpaolo_presta_id)
    transactions = []
    for p in playlists:
        print("PLAYLIST:", p['name'])
        transactions.append(get_playlist_artists(p['id']))
    for t in transactions:
        print(t)
        print()
    rules_mined = association_rules(transactions)
    print_rules(rules_mined)
             
if __name__ == "__main__":
  main()