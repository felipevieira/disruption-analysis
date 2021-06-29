import csv

import networkx as nx
from igraph import Graph
from networkx.drawing.nx_pylab import draw_networkx
from networkx.generators import directed

from face_validity import *

SONGS_PER_DECADE = 50
WINDOW_SIZE = 1000
def extract_disruptions(list_of_features, similarity_matrix):
    G = Graph(directed=True)
    count = 0
    with open("disruption_statistics.csv", "w") as disruption_csv:
        headers = ["id", "in", "out", "i", "j", "k", "disruption", "i_songs", "j_songs"]
        writer = csv.DictWriter(disruption_csv, fieldnames=headers)
        writer.writeheader()
        with open(list_of_features, 'r') as features:
            all_features = features.readlines()[1:]
            for i in range(len(all_features)):
                count+=1
                print("processing entry %i" % i)
                G = Graph(directed=True)
                song_id = all_features[i].split(",")[0]
                weights = []
                edges = []
                node_map = {}
                focal_node = G.add_vertex(idxfilelist=song_id, idxfeaturelist=i)
                node_map[song_id] = focal_node.index
                # i_song_year = int(all_features[i].split(",")[3])
                i_song_artist = all_features[i].split(",")[1]
                for sucessor in range(i, min(i + WINDOW_SIZE + 1, len(all_features))):
                    # sucessor_song_year = int(all_features[sucessor].split(",")[3])
                    sucessor_song_artist = all_features[sucessor].split(",")[1]
                    # if i_song_artist != sucessor_song_artist:
                    successor_song_id = all_features[sucessor].split(",")[0]
                    if not successor_song_id in node_map.keys():
                        node = G.add_vertex(idxfilelist=successor_song_id, idxfeaturelist=sucessor)
                        node_map[successor_song_id] = node.index
                    for predecessor in range(max(0, i - WINDOW_SIZE), i + 1):
                        # predecessor_song_year = int(all_features[predecessor].split(",")[3])
                        predecessor_song_artist = all_features[predecessor].split(",")[1]
                        if sucessor_song_artist != predecessor_song_artist:
                            predecessor_song_id = all_features[predecessor].split(",")[0]
                            if not predecessor_song_id in node_map.keys():
                                node = G.add_vertex(idxfilelist=predecessor_song_id, idxfeaturelist=predecessor)
                                node_map[predecessor_song_id] = node.index
                            edges.append((node_map[successor_song_id], node_map[predecessor_song_id]))
                            weights.append(similarity_matrix[sucessor, predecessor])
                G.add_edges(edges)
                G.es["weight"] = weights
                write_disruption_data(
                    writer,
                    focal_node,
                    get_disruption_for_node(focal_node, G, "../data/autoencoder/latent_representations-s100.csv")
                )

def write_disruption_data(writer, focal_node, data):
    writer.writerow({
        "id": focal_node.attributes()["idxfeaturelist"],
        "in": data[0],
        "out": data[1],
        "i": data[2],
        "j": data[3],
        "k": data[4],
        "disruption": data[5],
        "i_songs": ','.join([str(s) for s in data[6]]),
        "j_songs": ','.join([str(s) for s in data[7]])
    })

def get_disruption_for_node(focal_node, graph, listfiles):
    with open(listfiles, 'r') as list_of_files:
        song_files = list_of_files.readlines()
        i_count = 0
        j_count = 0
        k_count = 0
        i_songs = []
        j_songs = []
        # pra o nó sucessor ser do tipo "i" ele precisa ter uma similaridade
        # com o nó focal 7% maior que a média das similaridades desse nó sucessor com os antecessores do nó focal
        # 0.07 vem da validação
        threshold = 0.07

        for edge in focal_node.in_edges():
            sucessor_node = graph.vs[edge.source]
            edges_with_predecessors = sucessor_node.out_edges()
            average_similarities_with_predecessors = sum([edge.attributes()["weight"] for edge in edges_with_predecessors]) / len(edges_with_predecessors)
            similarity_with_focal_node = graph.es.find(_source=graph.vs[edge.source].index, _target=focal_node.index).attributes()["weight"]

            diff = similarity_with_focal_node - average_similarities_with_predecessors
            if diff >= 0 + threshold:
                i_count+=1
                i_songs.append(song_files[sucessor_node.attributes()["idxfeaturelist"]].split(",")[0])
            elif diff < 0 + threshold and diff > 0 - threshold:
                j_count+=1
                j_songs.append(song_files[sucessor_node.attributes()["idxfeaturelist"]].split(",")[0])
            else:
                k_count+=1

        disruption = (i_count - j_count) / (i_count + j_count + k_count) if (i_count + j_count + k_count) > 0 else 0
        return graph.degree(focal_node.index, mode="in"), graph.degree(focal_node.index, mode="out"), i_count, j_count, k_count, disruption, i_songs, j_songs

REGENERATE_NETWORK = True
if __name__ == "__main__":
    import collections

    features = load_features_from_file("../data/autoencoder/latent_representations-s100.csv")

    print("calculating similarity matrix...")
    sm = similarity_matrix_by_rbf(features, gamma=0.2)
    print(sm[9006][8981])

    print("generating network..")
    g = extract_disruptions("../data/autoencoder/latent_representations-s100.csv", sm)
