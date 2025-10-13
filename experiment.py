from spotify_kdtree import KDTree
import json
import pandas as pd
from dataReader import read_csv
import numpy as np
import spotipy 
from spotipy.oauth2 import SpotifyClientCredentials
import random
import matplotlib.pyplot as plt
import time

# using this so we can easily look up a song name and artist using a track id
# embedding got messed up so we only have the track ids and not all ids are in the csv dataset 
# give us easy access to song names and artists
CLIENT_ID = ''
CLIENT_SECRET = ''
client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)



def rec_analysis(trials):

    

    # loops through playlists in json file
    for i in range(trials):
        total_loc = [0] * 13
        playlist = getPlaylist_json(i)
        test_set = playlist['tracks']
        test_size = len(test_set)
        if test_size == 0:
            print("playlist was too short")
            continue
        embed_df = pd.read_csv("embedding.csv")
    
        id_list = []
            
        # for every song in our test set grab the track_id and put on a list
        for song in test_set:
            id_list.append(song['track_uri'].split(':')[-1])


        avg_fts = [0] * 13
        for track_id in id_list:
            # go into df and grab row as list
            location = embed_df[embed_df['track_id'] == track_id]
            if location.empty:
                # this shouldn't happen since all embedded songs
                print(f"Warning: no match found for track_id {track_id}")
                # skip this track if not found
                continue  
            
            # chop off the song ids
            location = location[1:]
            # add to cumulitive list
            for i in range(len(location[1:])):
                total_loc += location[i]
            
        # average location 
        avg_loc = [0]*13
        for i in range(len(total_loc)):
            avg_loc[i] = total_loc[i] / test_size
        
        avg_loc.insert(0, 'test')
        kd = KDTree(embed_df.to_numpy())
        
        nearest_dist, nearest_ID, check_box_nonexistent = kd.k_nearest(avg_loc, 5)
        print(nearest_dist, "is how close our graph comes to our average song point")
        print(nearest_ID, "is a nearby value to our average song point")














# using our json playlist data, this function loads file and retrieves playlist
# and returns playlist dictionary
def getPlaylist_json(i):
    with open("mpd.slice.0-999.json", "r") as f:
        data = json.load(f)
        playlists = data["playlists"]
        playlist = playlists[i]
        # print("Playlist name:", playlist["name"])
        # for track in playlist["tracks"]:
        #     print("-", track["track_name"], "by", track["artist_name"])
    return playlist

       

def qualitativeExperiment():
    # for this many playlists we can test our code by reccomending songs based on all but five songs from
    # from the playlist, and then compare our reccomendations to the five songs that weren't used
    song_num = []
    runtime = []
    avg_fts_diff = [0]*13
    playlist_count = 0
    for i in range(10):
        playlist_count += 1
        playlist = getPlaylist_json(i)
        test_set = playlist['tracks'][:-5]
        test_size = len(test_set)
        song_num.append(test_size)
        if test_size == 0:
            print("playlist was too short")
            continue
        actual = playlist['tracks'][-5:] 
        embedded_df = pd.read_csv("embedding.csv")
        id_list = []
        
        # for every song in our test set grab the track_id and put on a list
        for song in test_set:
            name = song['track_name']
            ids_df = read_csv()
            # under 'track_uri' is the song ID
            
            id_list.append(song['track_uri'].split(':')[-1])
            
            
        avg_fts = [0] * 13
        for track_id in id_list:
            
            # Find the row(s) matching this track_id
            matching_rows = embedded_df[embedded_df['track_id'] == track_id]

            if matching_rows.empty:
                print(f"Warning: no match found for track_id {track_id}")
                # skip this track if not found
                continue  

            # # Keep only numeric feature columns
            features_only = matching_rows.select_dtypes(include=np.number)

            # Get the numeric feature values as a 1D array
            feature_values = features_only.to_numpy()[0]

            # Add these values to the cumulative feature totals
            for i, value in enumerate(feature_values):
                avg_fts[i] += value
        
        # average all the features out base on how many songs we used
        print(test_size)
        for ft in avg_fts:
            ft // test_size


        kd = KDTree(embedded_df.to_numpy())

        avg_fts.insert(0, "test")
        nearest_dist, nearest_ID, check_box_nonexistent = kd.search(avg_fts)
        print(nearest_dist, "is how close our graph comes to our average song point")
        print(nearest_ID, "is a nearby value to our average song point")


        print(ids_df[ids_df['track_id'] == nearest_ID])
        print(embedded_df[embedded_df['track_id'] == nearest_ID])

        # Get track information
        track_info = sp.track(nearest_ID)

        # Extract the song name
        song_name = track_info['name']
        artist_names = [artist['name'] for artist in track_info['artists']]
        print("Playlist name:", playlist["name"])
        for track in playlist["tracks"]:
            print("-", track["track_name"], "by", track["artist_name"])
        print("The reccomended song is: ", song_name, " by ", artist_names)


        actual_avg_fts = [0] * 13
        # looking at our comparison songs that were not included in the reccomendation
        correct = False
        for songs in actual: 
            if song['track_name'] == song_name:
                correct = True
            matching_rows = embedded_df[embedded_df['track_id'] == song['track_uri'].split(':')[-1]]
            features_only = matching_rows.select_dtypes(include=np.number)
            feature_values = features_only.to_numpy()[0]

            # Add these values to the cumulative feature totals
            for i, value in enumerate(feature_values):
                actual_avg_fts[i] += value


        # actual_avg_fts = calc_avg_fts(actual, embedded_df)


        fts_diff = [0]*13
        avg_fts = avg_fts[1:]
        for i, ft in enumerate(actual_avg_fts):
            ft = ft
            fts_diff[i] = avg_fts[i] - ft

        fts_diff = [float(x) for x in fts_diff]
        
        print("reccomendation feature difference to actual features: ", fts_diff)
        print("graph proximity: ", nearest_dist)

        # adding the overall feature difference to a cumulitive list
        for i, ft in enumerate(avg_fts_diff):
            avg_fts_diff[i] = avg_fts_diff[i] + fts_diff[i]

    for i, ft in enumerate(avg_fts_diff):
            avg_fts_diff[i] = avg_fts_diff[i] // playlist_count
    feature_names = ["popularity", "duration_ms", "danceability", "energy", "loudness", "mode", "speechiness", "acousticness", "instrumentalness", "liveness", "valence", "tempo", "time_signature"]
    plot_feature_difference(avg_fts_diff, feature_names, playlist["name"])





#
#parameters = list of differences for each feature, feature names (optional), playlist title
#plots average feature difference between reccomended songs and actual songs take from playlist
#"""
def plot_feature_difference(fts_diff, feature_names=None, playlist_name="Playlist"):
    if feature_names is None:
        # default feature names
        feature_names = [f"Feature {i+1}" for i in range(len(fts_diff))]
    

    plt.figure(figsize=(10,6))
    plt.bar(feature_names, fts_diff, color='skyblue')
    plt.xlabel("Features")
    plt.ylabel("Average Difference")
    plt.title(f"Average Feature Difference for {playlist_name}")
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()



def runtime():
    embedded_df = pd.read_csv("embedding.csv")
    kd = KDTree(embedded_df.to_numpy())

    runtimes = []
    song_counts = []

    # trials
    for count in range(1, 501, 50): 
        start_time = time.time()
        for j in range(count):
            fts = embedded_df.iloc[j].to_numpy()
            kd.k_nearest(fts, j)
        end_time = time.time()

        runtimes.append(end_time - start_time)
        song_counts.append(count)

    # plot runtime vs number of songs
    plt.figure(figsize=(8, 5))
    plt.plot(song_counts, runtimes, marker='o')
    plt.title("Runtime vs Number of Songs Queried")
    plt.xlabel("Number of Songs Queried")
    plt.ylabel("Total Runtime (seconds)")
    plt.grid(True)
    plt.show()

    return runtimes, song_counts


            
            
            



    
# qualitativeExperiment()

runtime()


