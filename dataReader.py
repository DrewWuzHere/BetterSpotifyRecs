import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler


# returns a numpy array with the song and then all of the features following
def read_csv(genre):
    # whole dataframe
    df = pd.read_csv('dataset.csv')
    poss_styles = []
    for musicStyle in df['track_genre']:
         if musicStyle not in poss_styles:
             poss_styles.append(musicStyle)
    #print(poss_styles)
    my_df = df[df['track_genre'] == genre]

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






read_csv('british')
