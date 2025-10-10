
import networkx as nx
import json
import itertools
import matplotlib as plt
# building each songs in input track_data as a node
def build_graph_nodes(graph, track_data):
    for id in track_data:
        graph.add_node(id)
    return graph

# updating edge values between songs based on how often they appear together in playlist dataset
# loop through songs in playlist dataset. If that song also exist play list input playlist then append it to a list. 
# At the end of each playlist in dataset, add 1 to value of each songs edges that's in the list.
def build_graph_edges(graph, track_data, dataset):
        f = open(dataset)
        js = f.read()
        f.close()
        slice = json.loads(js)
        for tracks in slice["playlists"]:
            track_ids = []
            in_both = []
            for info in tracks["tracks"]:
                id = info["track_uri"]
                track_ids.append(id[14:])
            for song in track_data:
                    if song in track_ids:
                        in_both.append(song)
            for a, b in itertools.combinations(in_both, 2):
                if not graph.has_edge(a,b) or not graph.has_edge(b,a):
                    graph.add_edge(a, b, weight=1)
                else:
                    if graph.has_edge(a,b):
                        d = graph.get_edge_data(a,b)
                        new_w = d["weight"] + 1
                        graph.add_edge(a, b, weight= new_w)
                    elif graph.has_edge(b, a):
                        d = graph.get_edge_data(b,a)
                        new_w = d["weight"] + 1
                        graph.add_edge(b, a, weight= new_w)
        return graph


def get_tracks(dataset):
    track_data = []
    f = open(dataset)
    js = f.read()
    f.close()
    slice = json.loads(js)
    for tracks in slice["playlists"]:
        for info in tracks["tracks"]:
            id = info["track_uri"]
            if id not in track_data:
                track_data.append(id[14:])
    return track_data


def get_spring_layout(G, d):
     return nx.spring_layout(G, dim=d)

