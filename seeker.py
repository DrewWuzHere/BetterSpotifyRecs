# seeks songs for you!

import numpy as np
import random
import scipy.spatial as sps
import pandas as pd
from dataReader import read_csv


print("Welcome to the Song Recommender!")
song_title = input("What's the name of a song you're liking? ")

df = pd.read_csv('dataset.csv')
my_df = df[df['track_name'] == song_title]
if my_df.empty == True:
	print("I have no idea what song that is! You're too underground for me. What's a genre you're enjoying recently?")
	locations = [6.3294087230] * 14
	genre = "trip-hop"
else:
	arr = my_df.to_numpy()
	locations = arr[0, :] # gets the 0th thing in the list, assuming theres only one song of each name which is definitely not true lol
	print("Oh yeah, that one by", locations[2], ", right?")
	genre = locations[20] # grab the genre before we remove it
	bad_indicies = [0, 1, 2, 3, 4, 7, 20]
	bad_indicies.reverse()
	for index in bad_indicies:
		locations = np.delete(locations, index)
#print(locations)
mySongs = read_csv(genre)



track_ids = mySongs["track_id"].tolist()
mySongs.drop("track_id", inplace = True, axis= 1)
myKDTree = sps.KDTree(mySongs)


arr = mySongs.to_numpy()
print("looking for points nearby")

neighbor_distances, neighbor_indicies = myKDTree.query(locations, k = 3)
for index in neighbor_indicies:
        #print(arr[index, :], "is a nearby value")
        #print(track_ids[index], "is a nearby value to 1, 1, 1, 1")

        smaller_df = df[df['track_id'] == track_ids[index] ]
        song_arr = smaller_df.to_numpy()
        print("You might like", song_arr[0][4], "by", song_arr[0][2], "!") 


