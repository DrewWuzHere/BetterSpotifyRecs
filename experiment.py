from spotify_kdtree import KDTree
import scipy.spatial as sps
# import tracks_graph
import json
import pandas as pd
from dataReader import read_csv

def getPlaylist(i):
    with open("mpd.slice.0-999.filtered.json", "r") as f:
        data = json.load(f)
        playlists = data["playlists"]
        playlist = playlists[i]
        print("Playlist name:", playlist["name"])
        for track in playlist["tracks"]:
            print("-", track["track_name"], "by", track["artist_name"])
    return playlist
        

def runExpiriment():

    # for this many playlists we can test our code by reccomending songs based on all but five songs from
    # from the playlist, and then compare our reccomendations to the five songs that weren't used
    for i in range(1):
        playlist = getPlaylist(i)
        test_set = playlist['tracks'][:-5]
        predictions = playlist['tracks'][-5:] 
        my_df = read_csv()
        # loop through songs in test set and for each song get the track id from end of 'track_uri'
        # and then go to my_df and get the features and add them, avg_fts doesn't have track_ids
        avg_fts = pd.DataFrame(columns=my_df.columns.drop(['track_id','track_name']))
        avg_fts.loc[0] = 0 
        for song in test_set:
            name = song['track_name']
            # get features from data set
            # had to go by track name because IDs were being odd
            fts_row = my_df[my_df['track_name'] == name]
            print(name)
            if fts_row.empty:
                print("uh oh, track id didn't match a song")
                return
            fts_series = fts_row.drop(columns=['track_id', 'track_name']).iloc[0]
            print(fts_series)
            # drop track id and then add all the features together
            avg_fts.loc[0] = avg_fts.loc[0].add(fts_series, fill_value=0)

        
        # get average of features on the playlist
        avg_fts.loc[0] = avg_fts.loc[0] / len(test_set)
        
        # hand this point to kd tree to find neighbors/song recs
        my_df.drop(columns=['track_name'])
        kd = KDTree(my_df.to_numpy())
        nearest_dist, nearest_ID, check_box_nonexistent = kd.search(avg_fts)
        if check_box_nonexistent:
            print("welp")
        print(nearest_dist, "is how close our graph comes to our average song point")
        print(nearest_ID, "is a nearby value to our average song point")
        # recieve recs back and compare to predictions either by song title or by feature data


# print(getPlaylist())

runExpiriment()

def getSongFeatures():
    pass

