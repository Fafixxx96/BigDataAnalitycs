import sys
import spotipy
import spotipy.util as util


'''
Usage "python *script_name* gixs"

'''


idPlaylist = '4XoMUd3cPgLeazj8ezngUu';
username = ''

def show_tracks(tracks):
    for i, item in enumerate(tracks['items']):
        track = item['track']
        print("   %d %32.32s %s" % (i, track['artists'][0]['name'],
            track['name']))


if __name__ == '__main__':
    if len(sys.argv) > 1:
        username = sys.argv[1]
    else:
        print("Whoops, need your username!")
        print("usage: python user_playlists.py [username]")
        sys.exit()

    token = util.prompt_for_user_token(username)

    if token:
        sp = spotipy.Spotify(auth=token)

    else:
        print("Can't get token for", username)


    singlePlaylist = sp.user_playlist (user = username, playlist_id = idPlaylist, fields="tracks, next")
    tracks = singlePlaylist ['tracks']

    print ("Inizia lo show delle track")
    show_tracks(tracks)
    while tracks['next']:
        tracks = sp.next(tracks)
        show_tracks(tracks)