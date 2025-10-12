import numpy as np
import random
import scipy as scp
import pandas as pd

from dataReader import read_csv

class KDTree():

    def __init__(self, pts, a=1, depth=0):
        # look at the ath axis
        feats = pts[:, a]
        self.fc = None
        self.sc = None
        # sort our points according to that axis
        ft_sort = sorted(feats)
        # split the points along that axis
        split_val = ft_sort[len(ft_sort)//2] # i like this line cuz it covers the case where there's only one thing

        self.first_half = pts[ feats <  split_val  ]
        self.second_half = pts[ feats >  split_val  ]
        self.same = pts[feats == split_val] # points that exist on the split's axis
        self.same_points = {}
        for same_array in self.same:
            self.same_points[same_array[0]] = same_array[1:] # puts the 0th thing as the index and everything else as value (should it be other way round?)

        #plt.scatter(self.same[:, 0], self.same[:,1], c=depth)
        if self.first_half.shape[0] > 0:
            self.fc = KDTree( self.first_half, a = (a+1) % (pts.shape[1] - 1) + 1, depth=depth+1) # we write the axis weird cuz we never want it to be 0 as that's for track IDs
        if self.second_half.shape[0] > 0:
            self.sc = KDTree( self.second_half, a = (a+1) % (pts.shape[1] - 1) + 1, depth=depth+1) # we write the axis weird cuz we never want it to be 0 as that's for track ID
        self.a = a
        self.sp = split_val
        # recursively make new KDtrees with the two splits

    # given a location in kd space, find the closest point to it
    def search(self, new_fts): # assume new_fts doesn't have the track id with it, so it's the same size as a location in same_points
        if (self.fc == None and self.sc == None):
           print("found a leaf node, we should look along the axis that split to get to this point")
           check_box = False
           min_dist = np.sqrt(np.einsum('i, i->', new_fts[1:] - self.same[0][1:], new_fts[1:] - self.same[0][1:])) # gets the coordinates of the 0th thing in the list and finds distance to it
           closest_track = self.same[0][0] # track id of first item on the axis
           for key in self.same_points:
               poss_dist = np.sqrt(np.einsum('i, i->', new_fts[1:] - self.same_points[key], new_fts[1:] - self.same_points[key]))
               # poss_dist = scp.spatial.distance.cdist(new_fts, same_points[key]) # i think we want to get value from this key?
               if poss_dist < min_dist:
                   min_dist = poss_dist # saves the new minimum distance
                   closest_track = key
           if min_dist > abs(new_fts[self.a] - self.sp): # a'th coordinate of our point minus split point on that a-axis = distance to the line
               # search the other side of the box
               print(min_dist)
               check_box = True
           print("self.same is", self.same)
           print("went deeper, and check box came back", check_box)
           return min_dist, closest_track, check_box # check the other boxes anyway? when we break out of this loop


           # happens when we look for a song not in our dataset
           # never fear, just look for the self.same and then move our way back up the data tree!
        if self.fc != None and new_fts[self.a] < self.sp: # if new fts on axis a is less than the split point, it would have gone into the first half
            myMin, closestID, check_other_box = self.fc.search(new_fts)
            check_box = False
            if check_other_box and self.sc != None: # check the other box
                # search over self.sc.first_half and self.sc.second_half
                all_points = self.sc.first_half
                all_points = np.concatenate((all_points, self.sc.second_half))
                all_points = np.concatenate((all_points, self.sc.same))
                for key in all_points:
                    poss_dist = np.sqrt(np.einsum('i, i->', new_fts[1:] - key[1:], new_fts[1:] - key[1:] ))# i think we want to get value from this key?
                    if poss_dist < myMin:
                        print("the real min was on the other half!")
                        myMin = poss_dist # saves the new minimum distance
                        closestID = key[0]
            if myMin > abs(new_fts[self.a] - self.sp): # a'th coordinate of our point minus split point on that a-axis = distance to the line
                print(myMin)
                check_box = True # search the other side of the box
            print("went deeper, and check box came back", check_box)
            return myMin, closestID, check_box

        if self.sc != None and new_fts[self.a] > self.sp: # if new fts on axis a is the same as than the split point, it would have gone into the second half
            myMin, closestID, check_other_box = self.sc.search(new_fts)
            check_box = False
            if check_other_box and self.fc != None: # check the other box
                # search over self.fc.first_half and self.fc.second_half
                all_points = self.fc.first_half
                all_points = np.concatenate((all_points, self.fc.second_half), )
                all_points = np.concatenate((all_points, self.fc.same))
                for key in all_points:
                    poss_dist = np.sqrt(np.einsum('i, i->', new_fts[1:] - key[1:], new_fts[1:] - key[1:] )) # all_points isn't a dictionary, silly!
                    if poss_dist < myMin:
                        print("the real min was on the other half!")
                        myMin = poss_dist # saves the new minimum distance
                        closestID = key[0]
            if myMin > abs(new_fts[self.a] - self.sp): # a'th coordinate of our point minus split point on that a-axis = distance to the line
                print(myMin)

                check_box = True # search the other side of the box
            print("went deeper, and check box came back", check_box)
            return myMin, closestID, check_box


        if new_fts[self.a] == self.sp: # you were probably already in our list given how specific we are about coordinates, but the more the merrier. let's try to find your nearest points by looking for all the things in this box.
            # append all nodes from fc
            np.append(self.same, self.first_half)
            # append all nodes from sc
            np.append(self.same, self.second_half)
            check_box = False
            min_dist = np.sqrt(np.einsum('i, i->', new_fts[1:] - self.same[0][1:], new_fts[1:] - self.same[0][1:])) # gets the coordinates of the 0th thing in the list and finds distance to it
            closest_track = self.same[0][0] # track id of first item on the axis
            for key in self.same_points:
                poss_dist = np.sqrt(np.einsum('i, i->', new_fts[1:] - self.same_points[key], new_fts[1:] - self.same_points[key])) # i think we want to get value from this key?
                if poss_dist < min_dist:
                    min_dist = poss_dist # saves the new minimum distance
                    closest_track = key
            if min_dist == 0:
                print("Wow how creative you literally just plotted a point that's in our dataset")
                print(closest_track, "is the track id")
            if min_dist > abs(new_fts[self.a] - self.sp): # a'th coordinate of our point minus split point on that a-axis = distance to the line
                # search the other side of the box
                print(min_dist)

                check_box = True
            print("self.same is", self.same)
            print("went deeper, and check box came back", check_box)
            return min_dist, closest_track, check_box # check the other boxes anyway? when we break out of this loop



    def print(self):
        if (self.fc != None):
           self.fc.print()
        if (self.sc != None):
           self.fc.print()
        print(self.same, "at value", self.sp)

    def k_nearest(self, start_pt, k = 2): # for finding more than one nearby neighbor. if you just want one nearby neighbor, use search instead
        found_points = [0] * k
        mySmallerKDTree = self
        for i in range(k):
            myMin, closestID, check_box = mySmallerKDTree.search(start_pt)
            found_points[i] = closestID
            mySmallerSongs = read_csv()
            mySmallerSongs = mySmallerSongs.to_numpy()
            rowindex = 0
            for song in mySmallerSongs:
                if song[0] == closestID:
                    print("removing song ID", closestID)
                    mySmallerSongs = np.delete(mySmallerSongs, rowindex, axis = 0)
                rowindex += 1
            mySmallerKDTree = KDTree(mySmallerSongs) 
            # create a sub-kdtree with the closest point missing
            # this is tremendously inefficient at large k values probably
        return found_points      

# create some n-dimensional points
# array that the data lives in is a 2d array, but the KDTree is (or however many d)



my4dPoints = np.random.rand(100, 4)

mySongs = read_csv()
myKDTree = KDTree(mySongs.to_numpy())
for song in mySongs.to_numpy():
    if song[0] == '58q2HKrzhC3ozto2nDdN4z':
        print("cardi b")
        print(song)
'''
fourteen_ones = [0.896551724137931, 0.19694236611087584, 0.331, 0.341, 9, 0.2, 1, 0.0309, 0.528, 0.0, 0.109, 0.152, 0.3745400839508731, 0.5714285714285714]
# should give us back 0DuWDLjriRPjDRoPgaCslY, Adele's Love in the Dark
'''
'''
fourteen_ones = [0.9310344827586207, 0.41189982189052105, 0.556, 0.319, 9, 0.13751666666666665, 1, 0.0281, 0.893, 0.0, 0.0996, 0.294, 0.5110623878812041, 0.5714285714285714]

# should give back 3di5hcvxxciiqwMH1jarhY, Adele's Set Fire to the Rain, actually gives us back Someone like You from the same album. Is this a win?
'''
#fourteen_ones = ["yeah", 0.096774193549, 0.33011992630152964, 0.689, 0.739, 2, 0.09683333333333333, 1, 0.026, 0.0005, 0.6330845771144278, 0.064, 0.578, 0.45165831147704266, 0.5714285714285714]
# should give back gorillaz on melancholy hill (id 0q6LuUqGLUiCPP1cbdwFs3)
fourteen_ones = ["yeah", -0.0074945380203459665,0.028657416455284565,-0.01776030176370446,0.01601106398683131,0.016246769314095067,-0.1322633083242808,0.11479940947239312,-0.10706421770777681,-0.019097068030006565,-0.09454688315742632,-0.10544375112791222,0.10153541029951735,0.10730482143420414]
melancholy = ["on melancholy hill", -0.0074945380203459700, 0.028657416455284600, -0.01776030176370450, 0.01601106398683130, 0.016246769314095100,-0.1322633083242810, 0.11479940947239300, -0.10706421770777700, -0.019097068030006600, -0.09454688315742630, -0.10544375112791200, 0.10153541029951700, 0.10730482143420400]
print(mySongs.to_numpy().shape)

nearest_dist, nearest_ID, check_box_nonexistent = myKDTree.search(fourteen_ones)

if check_box_nonexistent:
    print("welp")
print(nearest_dist, "is how close our graph comes to [6.3294087230] * 14")
print(nearest_ID, "is a nearby value to [6.3294087230] * 14")
print(myKDTree.k_nearest(melancholy))
