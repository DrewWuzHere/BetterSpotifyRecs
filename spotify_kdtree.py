import numpy as np
import random
import scipy as scp
import pandas as pd
import heapq_max as heapq
import heapq as hq
import copy as cpy

class KDTree():
    '''
    KDTree.__init__(pts, a = 1, depth = 0): initialize a KDTree
    pts: a numpy array of k dimensions that contain the song ID at dimension 0 for each row. each row will become a point in our KDTree.
    a: used internally for the current axis we are iterating over. don't set this to 0 (song ID) or else things will probably break.
    depth: used internally to know what data type we should return.

    returns:
    a new KDtree object
    '''
    def __init__(self, pts, a=1, depth=0):
        if (depth == 0):
            track_ids = pts[:, 0]
            track_ids = track_ids.reshape(-1, 1)
            pts = np.round(pts[:, 1:].astype(np.float64), decimals = 8)
            #print("did pts round? pts[0][0] is", pts[0][0])
            pts = np.concatenate((track_ids, pts), axis = 1)
            #print("did pts round? pts[0][0] is", pts[0][1])

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
        if self.first_half.shape[0] > 0:
            self.fc = KDTree( self.first_half, a = (a+1) % (pts.shape[1] - 1) + 1, depth=depth+1) # we write the axis weird cuz we never want it to be 0 as that's for track IDs
        if self.second_half.shape[0] > 0:
            self.sc = KDTree( self.second_half, a = (a+1) % (pts.shape[1] - 1) + 1, depth=depth+1) # we write the axis weird cuz we never want it to be 0 as that's for track ID
        self.a = a
        self.sp = split_val
        # recursively make new KDtrees with the two splits

    '''
    KDTree.search(new_fts): given a location in kd space, find the closest point to it
    new_fts: an array with the same number of dimensions as the KDTree. new_fts should also have a song ID at the 0th dimension.

    returns: a tuple of: (the distance to the nearest node, the track ID of the nearest node, and a debugging variable that asks if a nearby box should be checked)

    this function handles multiple different cases for the current depth of the kd tree. multiple cases can be true simultaneously, regarding having both first and second children
    '''
    def search(self, new_fts):
        # case 1: leaf node
        if (self.fc == None and self.sc == None):
           #print("found a leaf node, we should look along the axis that split to get to this point")
           check_box = False
           min_dist = np.sqrt(np.einsum('i, i->', new_fts[1:] - self.same[0][1:], new_fts[1:] - self.same[0][1:])) # gets the coordinates of the 0th thing in the list and finds distance to it
           closest_track = self.same[0][0] # track id of first item on the axis
           for same_array in self.same:
               poss_dist = np.sqrt(np.einsum('i, i->', new_fts[1:] - same_array[1:], new_fts[1:] - same_array[1:]))
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
        # case 2: children
        elif (self.fc != None and new_fts[self.a] < self.sp ) or (self.sc != None and new_fts[self.a] > self.sp):
            if self.fc != None and new_fts[self.a] < self.sp: # if new fts on axis a is less than the split point, it would have gone into the first half
                #print("a is", self.a, "and same is", self.fc.same)
                myMin, closestID, check_other_box = self.fc.search(new_fts)
                check_box = False
                if check_other_box and self.sc != None: # check the other box
                    # search over self.sc.first_half and self.sc.second_half
                    all_points = self.sc.first_half
                    all_points = np.concatenate((all_points, self.sc.second_half))
                    all_points = np.concatenate((all_points, self.sc.same))
                    for key in all_points:
                        poss_dist = np.sqrt(np.einsum('i, i->', new_fts[1:] - key[1:], new_fts[1:] - key[1:] ))
                        if poss_dist < myMin:
                            print("the real min was on the other half!")
                            myMin = poss_dist # saves the new minimum distance
                            closestID = key[0] # gets the closest ID
                if myMin > abs(new_fts[self.a] - self.sp): # a'th coordinate of our point minus split point on that a-axis = distance to the line
                    print(myMin)
                    check_box = True # set a flag to search the other side of the box when we break out of this recursive call
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
                            #print("the real min was on the other half!")
                            myMin = poss_dist # saves the new minimum distance
                            closestID = key[0]
                if myMin > abs(new_fts[self.a] - self.sp): # a'th coordinate of our point minus split point on that a-axis = distance to the line
                    print(myMin)

                    check_box = True # search the other side of the box
                print("went deeper, and check box came back", check_box)
                return myMin, closestID, check_box


        elif new_fts[self.a] == self.sp: # you were probably already in our list given how specific we are about coordinates, but the more the merrier. let's try to find your nearest points by looking for all the things in this box.
            # append all nodes from fc
            np.append(self.same, self.first_half)
            # append all nodes from sc
            np.append(self.same, self.second_half)
            check_box = False
            min_dist = np.sqrt(np.einsum('i, i->', new_fts[1:] - self.same[0][1:], new_fts[1:] - self.same[0][1:])) # gets the coordinates of the 0th thing in the list and finds distance to it
            closest_track = self.same[0][0] # track id of first item on the axis
            for same_array in self.same:
                poss_dist = np.sqrt(np.einsum('i, i->', new_fts[1:] - same_array[1:], new_fts[1:] - same_array[1:])) # i think we want to get value from this key?
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
        else:
            check_box = False
            min_dist = np.sqrt(np.einsum('i, i->', new_fts[1:] - self.same[0][1:], new_fts[1:] - self.same[0][1:])) # gets the coordinates of the 0th thing in the list and finds distance to it
            closest_track = self.same[0][0] # track id of first item on the axis
            for same_array in self.same:
                poss_dist = np.sqrt(np.einsum('i, i->', new_fts[1:] - same_array[1:], new_fts[1:] - same_array[1:])) # i think we want to get value from this key?
                if poss_dist < min_dist:
                    min_dist = poss_dist # saves the new minimum distance
                    closest_track = key
            if min_dist > abs(new_fts[self.a] - self.sp): # a'th coordinate of our point minus split point on that a-axis = distance to the line
                # search the other side of the box
                print(min_dist)

                check_box = True
            #print("self.same is", self.same)
            #print("went deeper, and check box came back", check_box)
            return min_dist, closest_track, check_box # check the other boxes anyway? when we break out of this loop
            '''
            #print("new_fts[self.a] is", new_fts[self.a], "self.sp is", self.sp)
            #print("i genuinely don't know how this happened")
            #print("a is", self.a, "self.same is", self.same)
            #print("self.fc is", self.fc, "self.sc is", self.sc)
            #print("self.fc.same is", self.fc.same)
            #print("self.sp is", self.sp)
            return self.same
            '''

    def print(self):
        if (self.fc != None):
           self.fc.print()
        if (self.sc != None):
           self.fc.print()
        print(self.same, "at value", self.sp)

    def k_nearest_old(self, start_pt, k = 2): # for finding more than one nearby neighbor. if you just want one nearby neighbor, use search instead
        found_points = [0] * k
        mySmallerKDTree = self
        mySmallerSongs = pd.read_csv("embedding.csv")
        mySmallerSongs = mySmallerSongs.to_numpy()
        for i in range(k):
            myMin, closestID, check_box = mySmallerKDTree.search(start_pt)
            found_points[i] = closestID
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

    def k_nearest(self, new_fts, k = 2, depth = 0): # assume new_fts doesn't have the track id with it, so it's the same size as a location in same_points
        global nearest_points
        flag = False
        if depth == 0:
            #print("heyo!")
            flag = True
            nearest_points = DistanceHeap(k)
        #print("start of stackframe: depth is", depth)
        save_d = cpy.deepcopy(depth)
        if (self.fc == None and self.sc == None):
            #print("found a leaf node, we should look along the axis that split to get to this point")
            check_box = False
            min_dist = np.sqrt(np.einsum('i, i->', new_fts[1:] - self.same[0][1:], new_fts[1:] - self.same[0][1:])) # gets the coordinates of the 0th thing in the list and finds distance to it
            closest_track = self.same[0][0] # track id of first item on the axis
            for same_array in self.same:
                poss_dist = np.sqrt(np.einsum('i, i->', new_fts[1:] - same_array[1:], new_fts[1:] - same_array[1:]))
                if poss_dist < min_dist:
                    min_dist = poss_dist # saves the new minimum distance
                    closest_track = key
                    nearest_points.add(min_dist, closest_track)
            if min_dist > abs(new_fts[self.a] - self.sp): # a'th coordinate of our point minus split point on that a-axis = distance to the line
                # search the other side of the box
                #print(min_dist)
                check_box = True
            #print("self.same is", self.same)
            #print("went deeper, and check box came back", check_box)
            #print(flag)
            if flag:
                return list(nearest_points.track_ids.values())
            else:
                #print("depth is", depth)
                return nearest_points, check_box # check the other boxes anyway? when we break out of this loop

        elif (self.fc != None and new_fts[self.a] < self.sp) or (self.sc != None and new_fts[self.a] > self.sp):

           # happens when we look for a song not in our dataset
           # never fear, just look for the self.same and then move our way back up the data tree!
            if self.fc != None and new_fts[self.a] < self.sp: # if new fts on axis a is less than the split point, it would have gone into the first half
                nearest_points, check_other_box = self.fc.k_nearest(new_fts, k = k, depth = depth + 1)
                depth = save_d
                check_box = False
                if check_other_box and self.sc != None: # check the other box
                    # search over self.sc.first_half and self.sc.second_half
                    all_points = self.sc.first_half
                    all_points = np.concatenate((all_points, self.sc.second_half))
                    all_points = np.concatenate((all_points, self.sc.same))
                    for key in all_points:
                        poss_dist = np.sqrt(np.einsum('i, i->', new_fts[1:] - key[1:], new_fts[1:] - key[1:] ))# i think we want to get value from this key?
                        if poss_dist < nearest_points.get_max() :  # gets the largest distance in our heap
                            #print("the real min was on the other half!")
                            nearest_points.add(poss_dist, key[0]) # key[0] is the track id
                if nearest_points.get_max() > abs(new_fts[self.a] - self.sp): # a'th coordinate of our point minus split point on that a-axis = distance to the line
                    #print(nearest_points.get_max())
                    check_box = True # search the other side of the box
                #print("went deeper, and check box came back", check_box)
                #print(flag)

                if flag:
                    return list(nearest_points.track_ids.values())
                else:
                    #print("depth is", depth)
                    return nearest_points, check_box # check the other boxes anyway? when we break out of this loop

            if self.sc != None and new_fts[self.a] > self.sp: # if new fts on axis a is the same as than the split point, it would have gone into the second half
                nearest_points, check_other_box = self.sc.k_nearest(new_fts,k= k, depth = depth + 1)
                depth = save_d
                check_box = False
                if check_other_box and self.fc != None: # check the other box
                    # search over self.fc.first_half and self.fc.second_half
                    all_points = self.fc.first_half
                    all_points = np.concatenate((all_points, self.fc.second_half), )
                    all_points = np.concatenate((all_points, self.fc.same))
                    for key in all_points:
                        poss_dist = np.sqrt(np.einsum('i, i->', new_fts[1:] - key[1:], new_fts[1:] - key[1:] )) # all_points isn't a dictionary, silly!
                        if poss_dist < nearest_points.get_max():
                            #print("the real min was on the other half!")
                            nearest_points.add(poss_dist, key[0])
                if nearest_points.get_max() > abs(new_fts[self.a] - self.sp): # a'th coordinate of our point minus split point on that a-axis = distance to the line
                    #print(nearest_points.get_max())

                    check_box = True # search the other side of the box
            #print("went deeper, and check box came back", check_box)
            #print(flag)

                if flag:
                    return list(nearest_points.track_ids.values())
                else:
                    #print("depth is", depth)
                    return nearest_points, check_box # check the other boxes anyway? when we break out of this loop


        elif new_fts[self.a] == self.sp: # you were probably already in our list given how specific we are about coordinates, but the more the merrier. let's try to find your nearest points by looking for all the things in this box.
            # append all nodes from fc
            np.append(self.same, self.first_half)
            # append all nodes from sc
            np.append(self.same, self.second_half)
            check_box = False
            min_dist = np.sqrt(np.einsum('i, i->', new_fts[1:] - self.same[0][1:], new_fts[1:] - self.same[0][1:])) # gets the coordinates of the 0th thing in the list and finds distance to it
            closest_track = self.same[0][0] # track id of first item on the axis
            for same_array in self.same:
                poss_dist = np.sqrt(np.einsum('i, i->', new_fts[1:] - same_array[1:], new_fts[1:] - same_array[1:])) # i think we want to get value from this key?
                if poss_dist < min_dist:
                    min_dist = poss_dist # saves the new minimum distance
                    closest_track = key
                    nearest_points.add(min_dist, closest_track)

            if min_dist > abs(new_fts[self.a] - self.sp): # a'th coordinate of our point minus split point on that a-axis = distance to the line
                # search the other side of the box
                #print(min_dist)

                check_box = True
            #print("self.same is", self.same)
            #print("went deeper, and check box came back", check_box)
            #print(flag)

            if flag:
                return list(nearest_points.track_ids.values())
            else:
                #print("depth is", depth)
                return nearest_points, check_box # check the other boxes anyway? when we break out of this loop
        else:
            check_box = False
            min_dist = np.sqrt(np.einsum('i, i->', new_fts[1:] - self.same[0][1:], new_fts[1:] - self.same[0][1:])) # gets the coordinates of the 0th thing in the list and finds distance to it
            closest_track = self.same[0][0] # track id of first item on the axis
            for same_array in self.same:
                poss_dist = np.sqrt(np.einsum('i, i->', new_fts[1:] - same_array[1:], new_fts[1:] - same_array[1:])) # i think we want to get value from this key?
                if poss_dist < min_dist:
                    min_dist = poss_dist # saves the new minimum distance
                    closest_track = key
            if min_dist > abs(new_fts[self.a] - self.sp): # a'th coordinate of our point minus split point on that a-axis = distance to the line
                # search the other side of the box
                #print(min_dist)

                check_box = True
            #print("self.same is", self.same)
            #print("went deeper, and check box came back", check_box)
            #print(flag)

            if flag:
                return list(nearest_points.track_ids.values())
            else:
                #print("depth is", depth)
                return nearest_points, check_box # check the other boxes anyway? when we break out of this loop
# create some n-dimensional points
# array that the data lives in is a 2d array, but the KDTree is (or however many d)

class DistanceHeap():
    def __init__(self, maxLen):
        self.array = []
        heapq.heapify_max(self.array)
        self.track_ids = {}
        self.max = maxLen
    def add(self, newDistance, newID):
        if (len(self.array) >= self.max): # if the new item is less than the largest item in the heap, replace that largest item in the heap
            largest_dist = heapq.heapreplace_max(self.array, newDistance)
            del self.track_ids[largest_dist]
            self.track_ids[newDistance] = newID
        else:
            heapq.heappush_max(self.array, newDistance)
            self.track_ids[newDistance] = newID # hope and pray no two songs will have the exact same distance right
    def get_max(self):
        if len(self.array) < self.max:
            return 1e8 # very big negative number that our function is certainly smaller than
        return hq.nlargest(1, self.array)[0]


if __name__ == '__main__':
	mySongs = pd.read_csv("embedding.csv")
	myKDTree = KDTree(mySongs.to_numpy())
	melancholy_rounded = ['0q6LuUqGLUiCPP1cbdwFs3', -0.0074945380203459, 0.0286574164552845, -0.0177603017637044, 0.0160110639868313, 0.016246769314095, -0.1322633083242808, 0.1147994094723931, -0.1070642177077768, -0.0190970680300065, -0.0945468831574263, -0.1054437511279122, 0.1015354102995173, 0.1073048214342041]
	melancholy_direct = ['0q6blahblagblag', -0.0074945380203459700, 0.028657416455284600, -0.01776030176370450, 0.01601106398683130, 0.016246769314095100, -0.1322633083242810, 0.11479940947239300, -0.10706421770777700, -0.019097068030006600, -0.09454688315742630, -0.10544375112791200, 0.10153541029951700, 0.10730482143420400]
	problematic = ['test', -0.3694366641603041, -0.3694366641603041, -0.3694366641603041, -0.3694366641603041, -0.3694366641603041, -0.3694366641603041, -0.3694366641603041, -0.3694366641603041, -0.3694366641603041, -0.3694366641603041, -0.3694366641603041, -0.3694366641603041, -0.3694366641603041]
	kpop = ["kpop", 0.4891012663179000, 0.02485183999662070, 0.530648623551216, 0.5967799922446340, -0.6265789823999540, -0.44475631940318700, -0.4722187084061350, -0.3711020036499220, -0.2018788091408800, 0.5601040022588630, -0.5969632066789830, -0.5874018859276940, 0.3244325458370130]


#	print(mySongs.to_numpy().shape)
#	print(myKDTree.k_nearest(melancholy_rounded))
#	print(myKDTree.k_nearest(melancholy_direct))
	print(myKDTree.search(kpop))
	print(myKDTree.k_nearest(kpop, k=9))
