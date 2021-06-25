import networkx as nx
from networkx.drawing.nx_pylab import draw_networkx
import csv

from networkx.generators import directed
from face_validity import *
import time
import os
from igraph import Graph

SONGS_PER_DECADE = 50
def generate_network(list_of_features, similarity_matrix):
    G = Graph(directed=True)
    count = 0
    with open(list_of_features, 'r') as features:
        all_features = features.readlines()[1:]
        for i in range(len(all_features)):
            song_id = all_features[i].split(",")[0]
            G.add_vertex(name=int(song_id), index=i)
        weights = []
        for i in range(len(all_features)):
            count+=1
            print("processing entry %i" % i)
            song_id = all_features[i].split(",")[0]
            edges = []
            for j in range(i, 25605):
                if (i-1)!=(j-1):
                    i_song_year = int(all_features[i].split(",")[3])
                    j_song_year = int(all_features[j].split(",")[3])
                    i_song_artist = all_features[i].split(",")[1]
                    j_song_artist = all_features[j].split(",")[1]
                    # We only create an edge if songs are no more than 10 years apart and
                    # if they were sung by different artists
                    if (j_song_year - i_song_year)  <= 10 and (i_song_artist != j_song_artist):
                        edges.append((int(all_features[j].split(",")[0]), int(song_id)))
                        weights.append(similarity_matrix[j, i])
            G.add_edges(edges)
    G.es["weight"] = weights
    G.write_gml('network.gml')
    return G

def get_disruption_index_for_nodes(listfiles, graph):
    disruption_info = {}
    with open(listfiles, 'r') as list_of_files:
        song_files = list_of_files.readlines()
        for i in range(len(song_files)):
            print("calculating disruption for song %i" % i)
            if i == 0:
                continue
            song_id = int(song_files[i].split(",")[0])
            if graph.has_node(song_id):
                songs_after = [int(song.split(",")[0]) for song in song_files[i+1:]]
                song_influences = [edge[1] for edge in graph.edges(song_id)]

                ni = 0
                nj = 0
                nk = 0

                i_songs = []
                j_songs = []
                for song_after in songs_after:
                    consolidating_influence = False
                    if graph.has_edge(song_after , song_id):
                        for influence in song_influences:
                            if graph.has_edge(song_after, influence):
                                consolidating_influence = True
                                break
                        if consolidating_influence:
                            j_songs.append(song_after)
                            nj+=1
                        else:
                            i_songs.append(song_after)
                            ni+=1
                    else:
                        for influence in song_influences:
                            if graph.has_edge(song_after, influence):
                                nk+=1
                disruption_info[song_files[i]] = [graph.in_degree(song_id), graph.out_degree(song_id), ni, nj, nk, float((ni-nj)) / float((ni+nj+nk)), i_songs, j_songs] if (ni+nj+nk) > 0 else [graph.in_degree(song_id), graph.out_degree(song_id), ni, nj, nk, 0, i_songs, j_songs]
    return disruption_info

REGENERATE_NETWORK = True
if __name__ == "__main__":
    import collections

    # if REGENERATE_NETWORK:
    features = load_features_from_file("../data/autoencoder/latent_representations.csv")

    print("calculating similarity matrix...")
    sm = similarity_matrix_by_rbf(features, gamma=0.2)

    print("generating network..")
    g = generate_network("../data/autoencoder/latent_representations.csv", sm)
    # else:
    #     print("loading network...")
    #     g = nx.readwrite.gexf.read_gexf('window 10 - different artists - 0.80/network.gexf', node_type=int)


    # print("extracting disruption indexes...")
    # di = get_disruption_index_for_nodes("../data/autoencoder/latent_representations.csv", g)

    # sorted_x = sorted(di.items(), key=lambda kv: (kv[1][3], kv[1][0]), reverse=True)
    # sorted_dict = collections.OrderedDict(sorted_x)
    # print("writing disruptions to file...")
    # with open("disruption_statistics.csv", "w") as disruption_csv:
    #     headers = ["id", "in", "out", "i", "j", "k", "disruption", "i_songs", "j_songs"]
    #     writer = csv.DictWriter(disruption_csv, fieldnames=headers)
    #     writer.writeheader()
    #     for song in sorted_dict.keys():
    #         info = sorted_dict[song]
    #         writer.writerow({
    #             "id": int(song.split(",")[0]),
    #             "in": info[0],
    #             "out": info[1],
    #             "i": info[2],
    #             "j": info[3],
    #             "k": info[4],
    #             "disruption": info[5],
    #             "i_songs": ','.join([str(s) for s in info[6]]),
    #             "j_songs": ','.join([str(s) for s in info[7]])
    #         })
    #         # print("%s - %s" % (song.split(",")[0], sorted_dict[song]))
    # print("saving network...")
    # nx.write_gexf(g, "network.gexf")
