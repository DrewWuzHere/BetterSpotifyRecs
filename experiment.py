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
CLIENT_ID = '99f895fcb6fe44dbb5b58ecece413a2b'
CLIENT_SECRET = '70d4e35469ca4be489202a2e9064edf2'
client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


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

       
# this function reccomends a song for all but five songs on a playlist, it then compares the features of the reccomended song to 
# features of the five songs not included in the reccomendation. The results are plotted as a bar graph illustrating the difference in features.
#  Trials are the number of playlists you want to run this experiment for.
def qualitativeExperiment(trials):

    song_num = []
    avg_fts_diff = [0] * 13
    avg_dist = [0] * 13
    playlist_count = 0
    
    for i in range(trials):
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
            # under 'track_uri' is the song ID after the final colon
            id_list.append(song['track_uri'].split(':')[-1])
            
            
        avg_fts = [0] * 13
        for track_id in id_list:
            # Find the row(s) matching this track_id
            matching_rows = embedded_df[embedded_df['track_id'] == track_id]
            if matching_rows.empty:
                # this shouldn't happen since all embedded songs
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


        fts_diff = [0]*13
        avg_fts = avg_fts[1:]
        for i, ft in enumerate(actual_avg_fts):
            ft = ft
            fts_diff[i] = avg_fts[i] - ft

        fts_diff = [float(x) for x in fts_diff]
        
        print("reccomendation feature difference to actual features: ", fts_diff)
        print("graph proximity: ", nearest_dist)

        # adding the overall feature difference to a cumulitive list
        # and adding nearest_dist to cumulitive list
        for i, ft in enumerate(avg_fts_diff):
            avg_fts_diff[i] = avg_fts_diff[i] + fts_diff[i]
            # avg_dist = avg_dist[i] + nearest_dist



    # final averaging for feature difference and nearest distance
    for i, ft in enumerate(avg_fts_diff):
            avg_fts_diff[i] = avg_fts_diff[i] / playlist_count
            # avg_dist = float(avg_dist[i]) / playlist_count


    feature_names = ["popularity", "duration_ms", "danceability", "energy", "loudness", "mode", "speechiness", "acousticness", "instrumentalness", "liveness", "valence", "tempo", "time_signature"]
    plt.figure(1)
    titleOne = f"Average Feature Differences Between Reccomended Features and Actual Features"
    plot_feature_difference(avg_fts_diff, titleOne, feature_names)
    plt.figure(2)
    titleTwo = f"Avgerage Distance from Reccomended Song Features to Average Features from Test Playlists"
    plot_feature_difference(nearest_dist, titleTwo, feature_names)
    

    return



#
#parameters = list of differences for each feature, feature names (optional), playlist title
#plots average feature difference between reccomended songs and actual songs take from playlist
#"""
def plot_feature_difference(fts_diff, title, feature_names=None):
    if feature_names is None:
        # default feature names
        feature_names = [f"Feature {i+1}" for i in range(len(fts_diff))]
    

    plt.figure(figsize=(10,6))
    plt.bar(feature_names, fts_diff, color='skyblue')
    plt.xlabel("Features")
    plt.ylabel("Average Difference")
    plt.title(title)
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()


# this code finds k-nearest n
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
            # should this be j or should this be a constant
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





def rec_analysis(trials):
            
            # embed_df = pd.read_csv("embedding.csv")
            # kd = KDTree(embed_df.to_numpy())
            # location = [0.9] * 13
            # location.insert(0, "test")
            # nearest_list = kd.k_nearest(location, 5)
            


    song_num = []
    edges_num = []

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
            row = embed_df[embed_df['track_id'] == track_id]
            if not row.empty:
                location = row.iloc[0, 1:].tolist()
                
            
            if len(location) == 0:
                # this shouldn't happen since all embedded songs
                print(f"Warning: no match found for track_id {track_id}")
                # skip this track if not found
                continue  
                        
            # add to cumulitive list
            for s in range(len(location)):
                total_loc += location[s]
            
            
        # average location 
        avg_loc = [0]*13
        for j in range(len(total_loc)):
            print(total_loc[j])
            avg_loc[j] = total_loc[j] / test_size
        
        kd = KDTree(embed_df.to_numpy())

        avg_loc = [float(x) for x in avg_loc]
        avg_loc.insert(0, 'test')
        

        nearest_list = kd.k_nearest(avg_loc, 5)
        print()
        print(nearest_list, "is a nearby value to our average song point")
        print()

        network = pd.read_csv("edges(in).csv")

        # loop through ids in songs recs and if it is found in the csv then add the connections
        for id in nearest_list:
            connections = 0
            # if this is in a pair in the csv
            match = network[(network['track1'] == id) | (network['track2'] == id)]
            if not match.empty:
                connections += match['weight'].sum()
        
        song_num.append(test_size)
        edges_num.append(connections)
        print("connections: ", connections)
        print(song_num)
        print(edges_num)

    plt.figure(figsize=(8, 5))
    plt.plot(song_num, edges_num)
    plt.title("Playlist Connections vs Number of Songs Queried")
    plt.xlabel("Number of Songs")
    plt.ylabel("Times the Recommend Songs Appeared on Playlists with the Test Songs")
    plt.grid(True)
    plt.show()


rec_analysis(10)
    
# qualitativeExperiment(3)

# runtime()



# if five recs song appear in any playlist with the songs i do have, win
