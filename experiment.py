from spotify_kdtree import KDTree
import json
import pandas as pd
import matplotlib.pyplot as plt
import time
import operator


# using our json playlist data, this function loads file and retrieves playlistand returns playlist dictionary
# 'i' is the playlist number in the data set, range = 1-999
def getPlaylist_json(i):
    with open("mpd.slice.0-999.json", "r") as f:
        data = json.load(f)
        playlists = data["playlists"]
        print(len(playlists))
        playlist = playlists[i]
        print("Playlist name:", playlist["name"])
        for track in playlist["tracks"]:
            print("-", track["track_name"], "by", track["artist_name"])
    return playlist


# this code tracks and plots runtime of k-nearest function
def runtimeTest():
    embedded_df = pd.read_csv("embedding.csv")
    kd = KDTree(embedded_df.to_numpy())

    runtimes = []
    song_counts = []

    # 50 trials, for each trial find j number of neighbors 
    for count in range(1, 21): 
        for j in range(count):
            fts = embedded_df.iloc[40].to_numpy()
            start_time = time.time()
            kd.k_nearest(fts, j)
            end_time = time.time()

        runtimes.append(end_time - start_time)
        song_counts.append(count)

    # plot runtime vs number of songs
    plt.figure(figsize=(8, 5))
    plt.plot(song_counts, runtimes)
    plt.title("Runtime vs Number of Songs Queried")
    plt.xlabel("Number of Songs Queried")
    plt.ylabel("Total Runtime (seconds)")
    plt.grid(True)
    plt.show()

    return runtimes, song_counts


# plots how many time the recommended song is seen in a playlist from songs of the tests playlist
def qualityTest(trials):

    song_num = []
    edges_num = []

    # loops through playlists in json file
    for i in range(trials):
        i+= 1
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

        network = pd.read_csv("edges.csv")

        # loop through ids in songs recs and if it is found in the csv then add the connections
        total_conns = 0
        for song_id in nearest_list:
            match = network[(network['track1'] == song_id) | (network['track2'] == song_id)]
            match = match[(match['track1'].isin(id_list)) | (match['track2'].isin(id_list))]
            total_conns += match['weight'].sum()
        
        song_num.append(test_size)
        edges_num.append(total_conns)
    print("connections: ", total_conns)
    print(song_num)
    print(edges_num)
    
    # zipping together lists
    zipped = list(zip(song_num, edges_num)) 
    # sorting them
    res = sorted(zipped, key=operator.itemgetter(0))  
    # unzipped is a list of two lists song_num, edges_num)
    unzipped = [list(t) for t in zip(*res)] 
    song_num = unzipped[0]
    edges_num = unzipped[1]

    plt.figure(figsize=(10, 7))
    plt.scatter(song_num, edges_num)
    plt.title("Playlist Connections vs Number of Songs Queried")
    plt.xlabel("Number of Songs")
    plt.ylabel("Times the Recommend Songs Appeared on Playlists with the Test Songs")
    plt.grid(True)
    plt.show()


# gets "n" number of song reccommendations from the "playlist" dictionary
# returns reccomended song names
def getRec(n, playlist):

    # data set of songs
    with open("mpd.slice.0-999.json", "r") as f:
        data = json.load(f)
    allSongs_df = pd.json_normalize(data["playlists"], record_path="tracks")


    total_loc = [0] * 13
    test_set = playlist['tracks']
    test_size = len(test_set)
    if test_size == 0:
        print("playlist was too short")
        return
    embed_df = pd.read_csv("embedding.csv")
    id_list = []
        
    # for every song in our test set grab the track_id and put on a list
    for song in test_set:
        id_list.append(song['track_uri'].split(':')[-1])


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
        

    nearest_list = kd.k_nearest(avg_loc, n)
    print("Playlist name:", playlist["name"])
    for track in playlist["tracks"]:
        print("-", track["track_name"], "by", track["artist_name"])
    
    print()
    print("We think you might like")
    count = 1
    for song_id in nearest_list:
        track_info = allSongs_df[allSongs_df["track_uri"].str.split(":").str[-1] == song_id]
    
        print(f"{count}. {track_info['track_name'].iloc[0]} by {track_info['artist_name'].iloc[0]}")
        count += 1



# playlist = getPlaylist_json(22)
# getRec(5, playlist)
qualityTest(50)
# runtimeTest()
