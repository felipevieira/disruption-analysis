#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sklearn.metrics.pairwise import rbf_kernel
from scipy import spatial
import random
import csv

import numpy as np

LATENT_DIM = 500

def load_features_from_file(path):
        features = []
        headers = ["song_id", "artist_id", "artist_name", "year"]
        for i in range(LATENT_DIM):
                headers.append('latent-rep-%i' % (i+1))
        with open(path) as features_file:
                reader = csv.reader(features_file, headers)
                for row in reader:
                        if row[0] == "song_id":
                                continue
                        raw_features = [float(feature) for feature in row[4:]]
                        max_val = max(raw_features)
                        norm_features = [feature/max_val for feature in raw_features]
                        features.append(norm_features)
        return features

def similarity_matrix_by_rbf(feature_set, gamma=None):
        return rbf_kernel(feature_set, gamma=gamma)

def similarity_matrix_by_euclidean(feature_set):
        similarities = []
        for i in range(len(feature_set)):
                print("computing similarity matrix, entry %i" % i)
                i_sims = []
                for j in range(len(feature_set)):
                        i_sims.append(np.linalg.norm(np.array(feature_set[i]) - np.array(feature_set[j])))
                similarities.append(np.array(i_sims))
        return np.array(similarities)

def similarity_matrix_by_cosine(feature_set):
        similarities = []
        for i in range(len(feature_set)):
                print("computing similarity matrix, entry %i" % i)
                i_sims = []
                for j in range(len(feature_set)):
                        i_sims.append(1 - spatial.distance.cosine(feature_set[i], feature_set[j]))
                similarities.append(np.array(i_sims))
        return np.array(similarities)


def get_artist_indexes(artist_song, list_of_files):
        indexes = []

        artist_name = artist_song.split('/')[5].split('-')[0]
        with open(list_of_files, 'r') as list_of_files:
                all_files = list_of_files.readlines()
                for i in range(len(all_files)):
                        song_artist_name = all_files[i].split('/')[5].split('-')[0]
                        if all_files[i].split("|")[0].strip() == artist_song.strip():
                                continue
                        if song_artist_name == artist_name:
                                indexes.append(i)

        return indexes

def face_validity(path_features, similarity_matrix):
        total_checks = 0
        valid_checks = 0
        count = 0
        high_similarities = []
        all_features = open(path_features).readlines()[1:]
        with open(path_features) as features_file:
                with open("../data/r/intra-inter-similarities-s100-cosine.csv", "w") as csv_file:
                        reader = csv.reader(features_file)
                        writer = csv.DictWriter(csv_file, fieldnames=["song1_idx", "song2_idx", "song1_artist", "song2_artist", "similarity_type", "similarity"])
                        writer.writeheader()
                        for song_entry in reader:
                                count +=1
                                print("check %i of 25,605" %(count))
                                song_idx = reader.line_num - 2
                                if song_idx < 0:
                                        continue
                                artist_id = song_entry[1]
                                artist_name = song_entry[2]
                                with open(path_features) as features_file2:
                                        reader2 = csv.reader(features_file2)
                                        from_same_artist = []
                                        from_different_artist = []
                                        for song_entry2 in reader2:
                                                j = reader2.line_num - 2
                                                artist_id2 = song_entry2[1]
                                                if artist_id == artist_id2:
                                                        if j != song_idx:
                                                                from_same_artist.append(j)
                                                else:
                                                        from_different_artist.append(j)
                                if len(from_same_artist) > 10:
                                        total_checks += 1
                                        n_comparisons = 10
                                        sample_from_same_artists = random.sample(from_same_artist, n_comparisons)
                                        sample_from_differente_artists = random.sample(from_different_artist, n_comparisons)

                                        similarities_same_artist = [similarity_matrix[song_idx, song_from_same_artist_idx] for song_from_same_artist_idx in sample_from_same_artists]
                                        similarities_from_different_artist = [similarity_matrix[song_idx, song_from_different_artist_idx] for song_from_different_artist_idx in sample_from_differente_artists]

                                        average_same_artist = sum(similarities_same_artist) / len(similarities_same_artist)
                                        average_different_artist = sum(similarities_from_different_artist) / len(similarities_from_different_artist)

                                        for i in range(len(sample_from_same_artists)):
                                                writer.writerow({
                                                      "song1_idx": song_idx,
                                                      "song2_idx": sample_from_same_artists[i],
                                                      "song1_artist": artist_name,
                                                      "song2_artist": all_features[sample_from_same_artists[i]].split(",")[2],
                                                      "similarity_type": "intra-artist",
                                                      "similarity": similarities_same_artist[i]

                                                })
                                        for j in range(len(sample_from_same_artists)):
                                                writer.writerow({
                                                      "song1_idx": song_idx,
                                                      "song2_idx": sample_from_differente_artists[j],
                                                      "song1_artist": artist_name,
                                                      "song2_artist": all_features[sample_from_differente_artists[j]].split(",")[2],
                                                      "similarity_type": "inter-artist",
                                                      "similarity": similarities_from_different_artist[j]

                                                })
                                        high_similarities.append(average_same_artist)

                                        if average_same_artist > average_different_artist:
                                                valid_checks += 1

                        print("done! in %i of the %i times (%f%%) the check was valid" % (valid_checks, total_checks, (valid_checks*100/total_checks)))
                        print("the average similarity between songs from the same artist is %f" % (sum(high_similarities) / len(high_similarities)))



if __name__ == "__main__":
        features = load_features_from_file("../data/autoencoder/latent_representations-s100.csv")
        sm = similarity_matrix_by_cosine(features)
        # print(similarity_matrix_by_rbf(features, gamma=0.2))
        face_validity("../data/autoencoder/latent_representations-s100.csv", sm)