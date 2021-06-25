from os import write
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import tensorflow as tf
import matplotlib.pyplot as plt

from sklearn.metrics import accuracy_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from tensorflow.keras import layers, losses
from tensorflow.keras.datasets import fashion_mnist
from tensorflow.keras.models import Model

from array import array

import librosa.display

import csv

latent_dim = 500

class Autoencoder(Model):
  def __init__(self, latent_dim):
    super(Autoencoder, self).__init__()
    self.latent_dim = latent_dim
    self.encoder = tf.keras.Sequential([
      layers.Flatten(),
      layers.Dense(latent_dim),
    ])
    self.decoder = tf.keras.Sequential([
      layers.Dense(5000),
      layers.Reshape((10, 500))
      # layers.Dense(784, activation='sigmoid'),
      # layers.Reshape((28, 28))
    ])

  def call(self, x):
    encoded = self.encoder(x)
    decoded = self.decoder(encoded)
    return decoded

# from tensorflow.keras.datasets import fashion_mnist

# (train, _), (test, _) = fashion_mnist.load_data()

# train = train.astype('float32') / 255.
# test = test.astype('float32') / 255.

# print (type(train[0]))
# print (test.shape)

# print("reading dataset")
# dataset = pd.read_csv(
#   '../data/features [mfccs-2000].csv') \
#   .drop(['song_id', 'class', 'class_name'], axis=1)
# print("passou")

chunks = pd.read_csv(
  '../data/features [chroma-mfccs-10-500].csv', iterator=True, chunksize=1000)

print('reshaping...')
reshaped_dataset = []
chunk_count = 0
for chunk in chunks:
  print('reshaping a new chunk...')
  chunk_count+=1
  chunk = chunk.drop(['song_id', 'class', 'class_name'], axis=1)
  for idx, row in chunk.iterrows():
    reshaped_dataset.append(np.reshape(row.values.tolist(), (10, 500)))

dataset = np.asarray(reshaped_dataset)

train, test = train_test_split(dataset, test_size=0.2)

train = train.astype('float32') / 100.
test = test.astype('float32') / 100.

print('fitting model...')
autoencoder = Autoencoder(latent_dim)
autoencoder.compile(optimizer='adam', loss=losses.MeanSquaredError())
autoencoder.fit(train, train,
                epochs=200,
                shuffle=True,
                validation_data=(test, test))

encoded_songs = autoencoder.encoder(dataset).numpy()
decoded_songs = autoencoder.decoder(encoded_songs).numpy()

# Writing latent representations
print("writing %i entries to file... " % len(encoded_songs))
print(decoded_songs[0][0])
headers = ["song_id", "artist_id", "artist_name", "year"]
for i in range(latent_dim):
  headers.append('latent-rep-%i' % (i+1))
with open('../data/mfccs/features [mfcc statistics].csv', 'r') as features_file:
  with open('../data/autoencoder/latent_representations-s500.csv', 'w') as representations_file:
    with open('../data/list_songs.txt', 'r') as list_of_files:
      all_files = list_of_files.readlines()
      mfccs = features_file.readlines()
      writer = csv.DictWriter(representations_file, fieldnames=headers)
      writer.writeheader()
      for i in range(len(encoded_songs)):
        song = encoded_songs[i]
        latent_to_dict = {}
        latent_to_dict = {
          'song_id': mfccs[i+1].split(",")[0],
          'artist_id': mfccs[i+1].split(",")[1],
          'artist_name': mfccs[i+1].split(",")[2],
          'year': int(all_files[int(mfccs[i+1].split(",")[0]) - 1][0:4])
        }
        for j in range(latent_dim):
          latent_to_dict['latent-rep-%i' % (j+1)] = song[j]
        writer.writerow(latent_to_dict)


fig, ax = plt.subplots()
img = librosa.display.specshow(test[150], x_axis='time', ax=ax)
fig.colorbar(img, ax=ax)
ax.set(title='MFCC')
plt.savefig("[sample] original mfcc.png")

fig, ax = plt.subplots()
img = librosa.display.specshow(decoded_songs[150], x_axis='time', ax=ax)
fig.colorbar(img, ax=ax)
ax.set(title='MFCC')
plt.savefig("[sample] decoded mfcc.png")