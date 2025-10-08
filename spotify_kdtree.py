import numpy as np
import random
class KDTree():
    
    def __init__(self, pts, a=0, depth=0):
        # look at the ath axis
        feats = pts[:, a]
        self.fc = None
        self.sc = None
        # sort our points according to that axis
        ft_sort = sorted(feats)
        # split the points along that axis
        split_val = ft_sort[len(ft_sort)//2]
        
        first_half = pts[ feats <  split_val  ]
        second_half = pts[ feats >  split_val  ]
        self.same = pts[feats == split_val]
        
        #plt.scatter(self.same[:, 0], self.same[:,1], c=depth)
        
        if first_half.shape[0] > 0:
            self.fc = KDTree( first_half, a = (a+1) % pts.shape[1], depth=depth+1)
        if second_half.shape[0] > 0:
            self.sc = KDTree( second_half, a = (a+1) % pts.shape[1], depth=depth+1)
        self.a = a
        self.sp = split_val
        # recursively make new KDtrees with the two splits

    def search(self, new_fts):
        if (self.fc == None and self.sc == None):
           print("found a leaf node!")
        cand_lists = [self.same]
        if self.fc != None and new_fts[self.a] < self.sp:
            cand_lists.append(self.fc.search(new_fts))
        if self.sc != None and new_fts[self.a] > self.sp:
            cand_lists.append(self.sc.search(new_fts))
            
        candidates = np.concatenate(cand_lists)
        return candidates
    

    def print(self):
        if (self.fc != None):
           self.fc.print()
        if (self.sc != None):
           self.fc.print()
        print(self.same, "at value", self.sp)

def k_nearest(start_pt, search_tree, axis=0):
    # plot start_pt in k-space, or find the leaf nodes it's closest to 
    test_point = search_tree.sp
    nearby_points = []
    while (leafNodeFound == False):
        # if we don't have a first or second child we're at a leaf node which is the closest we'll get
        if (search_tree.fc == None and search_tree.sc == None):
            nearby_points.concatenate(self.same)
        if start_pt[axis] > test_point: # starts on the 0th axis
            # do the same thing with first_half on the 1st axis
            test_point = search_tree.fc.sp
            search_tree = search_tree.fc
            axis = (axis + 1) % search_tree.pts.shape[1] # number of feats we keep track of
        elif start_pt[axis] > test_point:
            # do the same thing with second_half on the 1st axis
            test_point = search_tree.sc.sp
            search_tree = search_tree.sc
            axis = (axis + 1) % search_tree.pts.shape[1] # number of feats we keep track of
        elif start_pt[axis] == test_point: # we found a matching point, so nearest neighbors must be somewhere nearby? do i need to take more into account?
            pass 
            # look for nearby leaf nodes 
            # how the heck do i look for nearby leaf nodes
            # find nearest neighbors to start_pt
            # return those points

# to find k nearest should I just delete the closest point from the list and then reconstruct it finding the second closest?


# create some n-dimensional points
# array that the data lives in is a 2d array, but the KDTree is (or however many d)

my4dPoints = np.random.rand(100, 4)
myKDTree = KDTree(my4dPoints)

myKDTree.print()

print("looking for points nearby")
print(myKDTree.search((1, 1, 1, 1)))
