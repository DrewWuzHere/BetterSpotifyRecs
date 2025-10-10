import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import json


# returns a numpy array with the song and then all of the features following
def read_csv(genre):

    df = pd.read_csv("dataset.csv")
    valid_tracks = set(df["track_name"])
    track_list = []

    with open("mpd.slice.0-999.json", "r") as f:
        data = json.load(f)
        for playlist in data["playlists"]:
            for track in playlist["tracks"]:
                if track["track_name"] in valid_tracks:
                    track_list.append(track["track_name"])  # <-- only track names

    # keeping all the songs that also are in the playlist data set
    df = df[df["track_name"].isin(track_list)]

    # taking songs we don't have features for out of json data set
    for playlist in data["playlists"]:
        new_tracks = []
        for t in playlist["tracks"]:
            if t["track_name"] in valid_tracks:
                new_tracks.append(t)
        playlist["tracks"] = new_tracks 

    # overwrite the file with the valid songs
    with open("mpd.slice.0-999.filtered.json", "w") as f:
        json.dump(data, f, indent=2)
    

    poss_styles = []
    for musicStyle in df['track_genre']:
         if musicStyle not in poss_styles:
             poss_styles.append(musicStyle)
    #print(poss_styles)
    my_df = df[df['track_genre'] == genre]
    print(my_df)
    print(df['track_genre'].unique())

    if my_df.empty:
        print(f"No tracks found for genre '{genre}' after filtering.")
        return None 

    # dataframe with only songs x features
    my_df = my_df.drop(['artists', 'album_name', 'track_name', 'explicit', 'track_genre', 'Unnamed: 0'], axis=1) 

    scaler = MinMaxScaler()
    my_df['popularity'] = scaler.fit_transform(my_df[['popularity']])
    my_df['duration_ms'] = scaler.fit_transform(my_df[['duration_ms']])
    my_df['tempo'] = scaler.fit_transform(my_df[['tempo']])
    my_df['instrumentalness'] = scaler.fit_transform(my_df[['instrumentalness']])
    my_df['time_signature'] = my_df[['time_signature']] / 7
    my_df['loudness'] = my_df[['loudness']] / -60


    arr = my_df.to_numpy()

    print(arr[0,:])
    print(arr[2,:])

    # track id, popularity, duration_ms, danceability, energy, key, loudness, mode, speechiness, acousticness, instrumentalness, liveness, valence, tempo, time_signature


    return my_df


# read_csv('rock')
