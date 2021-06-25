import os
import csv
import librosa
from librosa.feature.spectral import mfcc

from sklearn.metrics.pairwise import rbf_kernel


OUTPUT_PATH = '/home/felipe/workspace/disruption-analysis-website/data/magnatagatune/mp3/features [chroma-mfccs-10-100].csv'

FILE = open(OUTPUT_PATH, 'w', newline='')

DATASET_PATH = "/home/felipe/workspace/disruption-analysis-website/data/magnatagatune/mp3"
FEATURE_SIZE = 100
N_COEFFICIENTS = 10


headers = []
for coef in range(N_COEFFICIENTS):
    for value in range(FEATURE_SIZE):
        headers.append("mfcc-%i-%i" % (coef + 1, value + 1))
CSV_WRITER = csv.DictWriter(FILE, fieldnames=headers)
CSV_WRITER.writeheader()


def get_list_of_files(dir):
    subdirs = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "a", "b", "c", "d", "e", "f"]

    with open(os.path.join(DATASET_PATH, "list_of_files.txt"), "w") as list_of_files:
        for subdir in subdirs:
            for dirpath, dnames, fnames in os.walk(os.path.join(dir, subdir)):
                for f in fnames:
                    list_of_files.write("%s/%s\n" % (subdir, f))


def extract_mfcc_from_files(files_path):
    def write_to_file(mfccs):
        truncated_mfccs = [mfcc[:FEATURE_SIZE] for mfcc in mfccs]
        mfccs_dict = {}
        for coef in range(N_COEFFICIENTS):
            for value in range(FEATURE_SIZE):
                try:
                    mfccs_dict["mfcc-%i-%i" % (coef + 1, value + 1)] = truncated_mfccs[coef][value]
                except:
                    mfccs_dict["mfcc-%i-%i" % (coef + 1, value + 1)] = 0
        CSV_WRITER.writerow(mfccs_dict)

    with open(files_path, "r") as list_of_files:
        count = 0
        for f in list_of_files.readlines():
            full_song_path = os.path.join(DATASET_PATH, f).strip()
            y, sr = librosa.load(full_song_path)
            hop = int(librosa.get_duration(y) * sr / FEATURE_SIZE)
            mfccs = librosa.feature.mfcc(y=y, sr=sr, hop_length=hop, n_mfcc=N_COEFFICIENTS)
            write_to_file(mfccs)
            count += 1
            print("extracted %i of 25,853" % count)

def load_features_from_file(latent_ref_file):
    features = []
    with open(latent_ref_file) as features_file:
        for line in features_file.readlines()[1:]:
            feature = [float(rep) for rep in line.split(",")]
            features.append(feature)
    return features

def similarity_matrix_by_rbf(feature_set, gamma=None):
        return rbf_kernel(feature_set, gamma=gamma)


def get_dataset_index(path_list_of_files, file_name):
    with open(path_list_of_files) as list_of_files:
        return [str(entry).strip() for entry in list_of_files.readlines()].index(file_name)


# get_list_of_files(DATASET_PATH)
# extract_mfcc_from_files(os.path.join(DATASET_PATH, "list_of_files.txt"))

sm = similarity_matrix_by_rbf(load_features_from_file(
    "/home/felipe/workspace/disruption-analysis-website/data/magnatagatune/mp3/latent_representations.csv"),
    gamma=0.000001)

with open("/home/felipe/workspace/disruption-analysis-website/data/magnatagatune/comparisons_final_with_consensus.csv") as csv_comparisons:
    fieldnames = ['clip1_id', 'clip2_id', 'clip3_id', 'clip1_numvotes', 'clip2_numvotes', 'clip3_numvotes', 'clip1_mp3_path', 'clip2_mp3_path', 'clip3_mp3_path', '']
    reader = csv.DictReader(csv_comparisons, fieldnames=fieldnames)
    next(reader)
    count = 0
    trials = 0
    for row in reader:
        odd_idx = None
        max_votes = 0
        for i in [1,2,3]:
            if int(row['clip%i_numvotes' % i]) > max_votes:
                odd_idx = i
                max_votes = int(row['clip%s_numvotes' % i])
        similar_pair = [1,2,3]
        similar_pair.remove(odd_idx)
        dissimilar_pair = [odd_idx, similar_pair[0] if int(row["clip%i_numvotes" % similar_pair[0]]) > int(row["clip%i_numvotes" % similar_pair[1]]) else similar_pair[1]]

        dataset_idxs_similar = [get_dataset_index(
            "/home/felipe/workspace/disruption-analysis-website/data/magnatagatune/mp3/list_of_files.txt",
            row["clip%i_mp3_path" % idx]) for idx in similar_pair]
        dataset_idxs_dissimilar = [get_dataset_index(
            "/home/felipe/workspace/disruption-analysis-website/data/magnatagatune/mp3/list_of_files.txt",
            row["clip%i_mp3_path" % idx]) for idx in dissimilar_pair]
        trials += 1
        if sm[dataset_idxs_similar[0]][dataset_idxs_similar[1]] > sm[dataset_idxs_dissimilar[0]][dataset_idxs_dissimilar[1]]:
            count += 1

print("%i/%i (%f%%)" % (count, trials, (count*100/trials)))


