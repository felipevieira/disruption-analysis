
import csv
import os

import librosa

FEATURE_SIZE = 500
N_COEFFICIENTS = 10

OUTPUT_PATH = '/home/felipe/workspace/disruption-analysis-website/data/features [chroma-mfccs-10-500].csv'

FILE = open(OUTPUT_PATH, 'w', newline='')

class MFCCExtractor:
    def __init__(self, path_songs, path_list_all_songs):
        self.path_songs = path_songs
        self.path_list_all_songs = path_list_all_songs
        self.csv_writer = self._setup_writer()

    def _setup_writer(self):
        headers = ['song_id', 'class', 'class_name']
        for coef in range(N_COEFFICIENTS):
            for value in range(FEATURE_SIZE):
                headers.append("mfcc-%i-%i" % (coef + 1, value + 1))
        writer = csv.DictWriter(FILE, fieldnames=headers)
        writer.writeheader()
        return writer


    def extract(self):
        counter = 0
        with open(self.path_list_all_songs) as all_files:
            list_of_files = all_files.readlines()
            with open(self.path_songs, newline='') as csvfile:
                self.reader = csv.DictReader(csvfile)
                for row in self.reader:
                    idx = int(row['song_id']) - 1
                    song_row = list_of_files[idx].strip().split("|")
                    song_base = os.path.join(song_row[-2].strip(), song_row[-1].strip())
                    full_song_path = os.path.join("/home/felipe/Documents/PhD/forro em vinil resampled", song_base)
                    y, sr = librosa.load(full_song_path)
                    hop = int(librosa.get_duration(y) * sr / FEATURE_SIZE)
                    chromas = librosa.feature.mfcc(y=y, sr=sr, hop_length=hop, n_mfcc=10)
                    self.write_to_file(row, chromas)
                    counter+=1
                    print("%i/26,605" % counter)

    def write_to_file(self, row, mfccs):
        truncated_mfccs = [mfcc[:FEATURE_SIZE] for mfcc in mfccs]
        mfccs_dict = {}
        for coef in range(N_COEFFICIENTS):
            for value in range(FEATURE_SIZE):
                try:
                    mfccs_dict["mfcc-%i-%i" % (coef + 1, value + 1)] = truncated_mfccs[coef][value]
                except:
                    mfccs_dict["mfcc-%i-%i" % (coef + 1, value + 1)] = 0
        mfccs_dict['song_id'] = row['song_id']
        mfccs_dict['class'] = row['class']
        mfccs_dict['class_name'] = row['class_name']
        self.csv_writer.writerow(mfccs_dict)

extractor = MFCCExtractor(
    "/home/felipe/workspace/disruption-analysis-website/data/mfccs/features [mfcc statistics].csv",
    "/home/felipe/workspace/disruption-analysis-website/data/list_songs.txt")
extractor.extract()
