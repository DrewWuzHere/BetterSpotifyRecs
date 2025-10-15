# BetterSpotifyRecs
Better Spotify Recs is a recommendation algorithm that generates k recommeded songs.

## Description
Better Spotify Recs is built on a spotify playlist set of 1000 playlists. It embeds this data and uses a KD Tree to reccomend the k-nearest songs. Also attached are three experiments for the code to illustrate it's accuracy, runtime, and embedding.

## Getting Started

### Dependencies Needed

* libraries used:
  - json
  - pandas
  - matplotlib.pyplot
  - time
  - operator
  - numpy
  - scipy
  - networkx
  - itertools
  - heapq
  - heapq_max
  - copy


### Executing program

* After downloading zip file:
* run experiment() for short interactive terminal recommendation program
* experiment() also contains commented code at bottom for running various experiments
* seeker() contains commented code that will print the k-nearest points demonstrating KD Tree functionality


## Other

### File descriptions

* experiment.py
  - holds two types of experiments that can be run by uncommenting the last lines
* spotify_kdtree.py
  - containes KD Tree data structure and search functions
* seeker.py
  - given a point, can find the nearest point
* tracks_graph.py
  - Handles embedding songs into networkx based on playlist connections and creates embedding.csv

* playlist_data Folder and mpd.slic.0-999.json
  - playlist and song data used for embedding
* embedding.csv
  - track ids followed by 13 floats that represent dimension locations
 
* underground_test.ipynb
  - jupyter lab notebook illustrating the underground song experiment
* graph_tester.ipynb
  - jupyter lab notebook illustrating the embedding process
* experiment.ipynb
  - jupyter lab notebook illustrating runtime and song rec quality experiments
    




   











