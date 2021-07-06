import os
import sys
import csv
import json

def walk_on_files(dataset_path):
    dirs = [x[0] for x in os.walk(dataset_path)]
    metadata_json = {
        'albums': []
    }
    # with open('network_statistics.csv', newline='') as csv_network:
    #     with open('disruption_statistics.csv', newline='') as csv_disruption:
    count = 1
    for folder in dirs:
        print("parsing %i out of %i" %(count, len(dirs)))
        if folder == dataset_path:
            continue
        album_metadata = {
            'songs': _get_songs(dataset_path, folder),
            'picture': _get_picture(folder)
        }
        album_metadata.update(_get_album_metadata(os.path.basename(folder)))
        if len(album_metadata["songs"]) > 0:
            metadata_json['albums'].append(album_metadata)
        count += 1
    with open('out.txt', 'w') as file:
        file.write(json.dumps(metadata_json))

def _get_album_metadata(path):
    corner_cases = {
        '[1983] - 1983 - Negrão dos oito baixos (Forró em vinil)' : {
            'name': 'Negrão dos oito baixos',
            'artist': 'Negrão dos oito baixos',
            'year': 1983
        },
        '[1981] - 1981 - Sandro Becker vol.1 (Forró em vinil)' : {
            'name': 'Sandro Becker vol. 1',
            'artist': 'Sandro Becker',
            'year': 1981
        },
        '[1982] - 1982 - Sandro Becker vol.2 (Forró em vinil)' : {
            'name': 'Sandro Becker vol. 2',
            'artist': 'Sandro Becker',
            'year': 1982
        },
        '[1983] - 1983 - Sandro Becker vol.3 (Forró em vinil)' : {
            'name': 'Sandro Becker vol. 3',
            'artist': 'Sandro Becker',
            'year': 1983
        },
        '[1984] - 1984 - Sandro Becker vol.4 (Forró em vinil)' : {
            'name': 'Sandro Becker vol. 4',
            'artist': 'Sandro Becker',
            'year': 1984
        },
        '[1987] - 1987 - Sandro Becker vol7 (Forró em vinil)' : {
            'name': 'Sandro Becker vol. 7',
            'artist': 'Sandro Becker',
            'year': 1987
        },
        '[1988] - 1988 - Sandro Becker vol.8 (Forró em vinil)' : {
            'name': 'Sandro Becker vol. 8',
            'artist': 'Sandro Becker',
            'year': 1988
        },
        '[1985] - 1985 - Sandro Becker vol. 5 (Forró em vinil)' : {
            'name': 'Sandro Becker vol. 5',
            'artist': 'Sandro Becker',
            'year': 1985
        },
        '[1989] - 1989 - Sandro Becker vol.9 - Para presidente (Forró em vinil)' : {
            'name': 'Sandro Becker vol. 9',
            'artist': 'Sandro Becker',
            'year': 1989
        },
        '[2012] - Trio Marajó - Santo Antônio 2012 Via Show (Forró em vinil)' : {
            'name': 'Santo Antônio 2012 Via Show ',
            'artist': 'Trio Marajó',
            'year': 2012
        },
        '[2003] - 2003 - Benício Guimarães (Forró em vinil)' : {
            'name': 'Santo Antônio 2012 Via Show',
            'artist': 'Benício Guimarães',
            'year': 2003
        },
        '[1972] - Trio Sertanejo 1972 - Compacto duplo (Forró em vinil)' : {
            'name': 'Compacto duplo',
            'artist': 'Trio Sertanejo',
            'year': 1972
        },
        '[2010] - Baixinho dos Oito Baixos - 2010 (Forró em vinil)' : {
            'name': 'Baixinho dos Oito Baixos',
            'artist': 'Baixinho dos Oito Baixos',
            'year': 2010
        },
        '[1981] - Compacto duplo 1981 - Dominguinhos - Querubim (Forró em vinil)' : {
            'name': 'Compacto duplo',
            'artist': 'Dominguinhos',
            'year': 1981
        },
        '[1994] - Novinho da Paraíba - 1994 (Forró em vinil.com)' : {
            'name': 'Novinho da Paraíba ',
            'artist': 'Novinho da Paraíba ',
            'year': 1994
        },
        '[2015] - Cara de Doido - EP (2015) (Forró em vinil)' : {
            'name': 'Cara de Doido',
            'artist': 'Cara de Doido',
            'year': 2015
        },
        '[1981] - Bandinha de Pífano Cultural de Caruarú - 1981 (Forró em vinil)' : {
            'name': 'Bandinha de Pífano Cultural de Caruarú',
            'artist': 'Bandinha de Pífano Cultural de Caruarú',
            'year': 1981
        },
        '[1982] - ze da onca forro danado 1982 cid (forro em vinil)' : {
            'name': 'Forró Danado',
            'artist': 'Zé da Onça',
            'year': 1982
        },
        '[1990] - Zé Paraíba - O 1990 - Melhor do Forró (Forró em vinil)' : {
            'name': 'Ze Paraíba',
            'artist': 'O Melhor do Forró',
            'year': 1990
        }
    }

    if path in corner_cases.keys():
        return corner_cases[path]
    splitted = path.split("-")
    if len(splitted) < 4:
        if len(splitted) == 3:
            try:
                int(splitted[1])
                return {
                    'name': splitted[2].replace("(Forró em vinil)", "").replace("(forró em vinil)", "").strip(),
                    'artist': splitted[2].replace("(Forró em vinil)", "").replace("(forró em vinil)", "").strip(),
                    'year': int(splitted[0].replace("[", "").replace("]", "").replace("(forró em vinil)", "").strip())
                }
            except:
                return {
                    'name': splitted[1].replace("(Forró em vinil)", "").replace("(forró em vinil)", "").strip(),
                    'artist': splitted[1].replace("(Forró em vinil)", "").replace("(forró em vinil)", "").strip(),
                    'year': int(splitted[0].replace("[", "").replace("]", "").replace("(forró em vinil)", "").strip())
                }
        return {
            'name': splitted[2].replace("(Forró em vinil)", "").replace("(forró em vinil)", "").strip(),
            'artist': splitted[2].replace("(Forró em vinil)", "").replace("(forró em vinil)", "").strip(),
            'year': int(splitted[1].replace("(Forró em vinil)", "").replace("(forró em vinil)", "").strip())
        }
    try:
        return {
            'name': splitted[3].replace("(Forró em vinil)", "").replace("(forró em vinil)", "").strip(),
            'artist': splitted[1].replace("(Forró em vinil)", "").replace("(forró em vinil)", "").strip(),
            'year': int(splitted[2].replace("(Forró em vinil)", "").replace("(forró em vinil)", "").strip())
        }
    except:
        try:
            return {
                'name': splitted[3].replace("(Forró em vinil)", "").replace("(forró em vinil)", "").strip(),
                'artist': splitted[2].replace("(Forró em vinil)", "").replace("(forró em vinil)", "").strip(),
                'year': int(splitted[1].replace("(Forró em vinil)", "").replace("(forró em vinil)", "").strip())
            }
        except:
            return {
                'name': splitted[2].replace("(Forró em vinil)", "").replace("(forró em vinil)", "").strip(),
                'artist': splitted[1].replace("(Forró em vinil)", "").replace("(forró em vinil)", "").strip(),
                'year': int(splitted[3].replace("(Forró em vinil)", "").replace("(forró em vinil)", "").strip())
            }

def _get_songs(dataset_path, path):
    from random import uniform, randint
    audio_files = [f for f in os.listdir(path)
                if os.path.isfile(os.path.join(path, f))
                and (f.endswith(".mp3") or f.endswith(".wma"))]
    songs_info = []
    for audio_file in audio_files:
        with open('../data/misc/remote_urls.csv') as csvfile:
            fieldnames = ['file_path', 'url']
            csv_reader = csv.DictReader(csvfile, fieldnames=fieldnames)
            audio_file = audio_file.replace(dataset_path, '')
            csv_reader = csv.DictReader(csvfile, fieldnames=fieldnames)
            for row in csv_reader:
                if audio_file.strip() in row['file_path']:
                    song_id = _get_song_id(os.path.join(path.split("/")[-1], audio_file))
                    disruption_data = _get_disruption_data(song_id)
                    if disruption_data:
                        songs_info.append({
                            'id': song_id,
                            'title': _clear_song_name(audio_file).replace(".mp3", "").replace(".wma", ""),
                            'url': row['url'],
                            'disruption_index': round(float(disruption_data[5]), 2),
                            'in_degree': int(disruption_data[0]),
                            'out_degree': int(disruption_data[1]),
                            'degree': int(disruption_data[0]) + int(disruption_data[1]),
                            'ni': int(disruption_data[2]),
                            'nj': int(disruption_data[3]),
                            'nk': int(disruption_data[4])
                        })
    return songs_info

def _clear_song_name(song_filename):
    first_char_idx = 0
    for char in song_filename:
        if str.isalpha(char):
            break
        first_char_idx+=1
    if len(song_filename[first_char_idx:]) > 0:
        return song_filename[first_char_idx:]
    return song_filename


def _get_song_id(song_path):
    with open('list_songs.txt', 'r') as list_files:
        lines = list_files.readlines()
        for i in range(len(lines)) :
            splitted = lines[i].split("|")
            if song_path == os.path.join(splitted[-2].strip(), splitted[-1].strip()):
                return i + 1
    return -1

def _get_network_data(song_id):
    with open('network_statistics.csv', newline='') as csv_network:
        reader = csv.DictReader(csv_network)
        for row in reader:
            if int(row['Id']) == int(song_id):
                return [
                    row['indegree'],
                    row['outdegree'],
                    row['Degree']
                ]

def _get_disruption_data(song_id):
    with open('disruption_statistics.csv', newline='') as disruption_network:
        reader = csv.DictReader(disruption_network)
        for row in reader:
            if int(row['id']) == int(song_id):
                return [
                    row['in'],
                    row['out'],
                    row['i'],
                    row['j'],
                    row['k'],
                    row['disruption']
                ]

def _get_picture(path):
    pictures = [os.path.join(path, f) for f in os.listdir(path)
                if os.path.isfile(os.path.join(path, f))
                and (f.endswith(".jpeg") or f.endswith(".jpg") or f.endswith(".png") or f.endswith(".PNG") or f.endswith(".JPG") or f.endswith(".JPEG") or f.endswith(".gif") or f.endswith(".JPEG"))]
    for picture in pictures:
        if "capa" in picture or "Capa" in picture or "CAPA" in picture or "frente" in picture or "Frente" in picture or "FRENTE" in picture:
            pictures = [picture]
            break
    if len(pictures) < 1:
                return "https://i.pinimg.com/originals/7a/fc/02/7afc0212e8007796b4577cd6f9f0e106.png"
    with open('../data/misc/covers.csv') as csvfile:
            fieldnames = ['file_path', 'url']
            csv_reader = csv.DictReader(csvfile, fieldnames=fieldnames)
            for row in csv_reader:
                if pictures[0].strip() in row['file_path']:
                    return row['url']
    return ""

if __name__ == "__main__":
    walk_on_files(sys.argv[1])
