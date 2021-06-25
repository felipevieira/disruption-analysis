import sys
import csv
import unidecode


def walk_on_songs(songs_file_path, features_file_path):
    artist_counter = 0
    artist_map = {}
    with open('training_data.csv', 'w', newline='') as csvfile:
        fieldnames = ['song_id', 'class', 'class_name']
        for i in range(1, 161):
            print(i)
            fieldnames.append('mfcc-%i' % i)
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        with open(songs_file_path) as songs_file:
            list_of_songs = songs_file.readlines()
            with open(features_file_path) as features_file:
                list_of_features = features_file.readlines()
                for song_index in range(len(list_of_songs)):
                    song = list_of_songs[song_index]
                    album = song.split("|")[1]
                    artist = unidecode.unidecode(album.split("-")[1].strip().replace(" ","").lower())
                    if artist.isdigit():
                        artist = unidecode.unidecode(album.split("-")[2].strip().replace(" ","").lower())
                    if artist in artist_map.keys():
                        artist_id = artist_map[artist]
                    else:
                        artist_id = artist_counter
                        artist_map[artist] = artist_id
                        artist_counter+=1
                    features = [float(i) for i in list_of_features[song_index].split()]
                    song_data = {'song_id': song_index + 1, 'class': artist_id, 'class_name': artist}
                    for feature_idx in range(len(features)):
                        song_data['mfcc-%i' % (feature_idx+1)] = features[feature_idx]
                    writer.writerow(song_data)


if __name__ == "__main__":
    song_list_path = sys.argv[1]
    feature_list_path = sys.argv[2]

    walk_on_songs(song_list_path, feature_list_path)