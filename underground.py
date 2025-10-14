import json
import itertools
import pandas as pd

def artist_songs(artist_uri, dataset):
    artist = artist_uri
    f = open(dataset)
    js = f.read()
    f.close()
    slice = json.loads(js)
    track_ids = []
    for tracks in slice["playlists"]:
        for info in tracks["tracks"]:
            id = info["track_uri"][14:]
            art_id = info["artist_uri"][15:]
            if(art_id == artist) and id not in track_ids:
                track_ids.append(id)
    return track_ids

def song_distance(embedding, s_ids):
    pos = []
    df = pd.read_csv(embedding)
    for id in s_ids:
        track = df[df["track_id"].astype(str) == id]
        pos.append({"track_id": track["track_id"].iloc[0], "d1": track["d1"].iloc[0], "d2": track["d2"].iloc[0], "d3": track["d3"].iloc[0]
                    , "d4": track["d4"].iloc[0], "d5":track["d5"].iloc[0], "d6": track["d6"].iloc[0], "d7": track["d7"].iloc[0]
                    , "d8": track["d8"].iloc[0], "d9": track["d9"].iloc[0], "d10": track["d10"].iloc[0], "d11": track["d11"].iloc[0]
                    , "d12": track["d12"].iloc[0], "d13": track["d13"].iloc[0]})
    sum_d1, sum_d2, sum_d3, sum_d4, sum_d5, sum_d6, sum_d7, sum_d8, sum_d9, sum_d10, sum_d11, sum_d12, sum_d13 = 0,0,0,0,0,0,0,0,0,0,0,0,0
    for i in range(len(pos)):
        sum_d1 += pos[i]["d1"]
        sum_d2 += pos[i]["d2"]
        sum_d3 += pos[i]["d3"]
        sum_d4 += pos[i]["d4"]
        sum_d5 += pos[i]["d5"]
        sum_d6 += pos[i]["d6"]
        sum_d7 += pos[i]["d7"]
        sum_d8 += pos[i]["d8"]
        sum_d9 += pos[i]["d9"]
        sum_d10 += pos[i]["d10"]
        sum_d11 += pos[i]["d11"]
        sum_d12 += pos[i]["d12"]
        sum_d13 += pos[i]["d13"]
    n = len(pos)
    avg_d1 = sum_d1 / n
    avg_d2 = sum_d2 / n
    avg_d3 = sum_d3 / n
    avg_d4 = sum_d4 / n
    avg_d5 = sum_d5 / n
    avg_d6 = sum_d6 / n
    avg_d7 = sum_d7 / n
    avg_d8 = sum_d8 / n
    avg_d9 = sum_d9 / n
    avg_d10 = sum_d10 / n
    avg_d11 = sum_d11 / n
    avg_d12 = sum_d12 / n
    avg_d13 = sum_d13 / n
    pos_list = [avg_d1, avg_d2, avg_d3, avg_d4, avg_d5, avg_d6, avg_d7, avg_d8, avg_d9, avg_d10, avg_d11, avg_d12, avg_d13]
    return pos_list
