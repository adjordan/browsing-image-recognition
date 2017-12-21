import numpy as np
import csv
import math
from keras.layers import Dense
from keras.models import Sequential, load_model
from keras.applications.inception_v3 import InceptionV3

from PIL import Image
import requests
from io import BytesIO
import time
import random

random.seed(1)

hit_labels = ["/m/012c9l", "/m/0172jz", "/m/017fsk",
              "/m/01nq_x", "/m/01pdqb", "/m/01yrx",
              "/m/02rcwpb", "/m/03bw_6d", "/m/03c_ndy",
              "/m/03dj64", "/m/06jdsz", "/m/07k6w8",
              "/m/08x9c0", "/m/0cdnk", "/m/0g4cd0",
              "/m/0gvvmf6", "/m/0k8hs", ]

train_path = "/home/austin/Github/browsing-image-recognition/OpenImages/compiled-images/train/compiled-with-class.csv"
val_path = "/home/austin/Github/browsing-image-recognition/OpenImages/compiled-images/validate/compiled.csv"
test_path = "/home/austin/Github/browsing-image-recognition/OpenImages/compiled-images/test/compiled.csv"


def initialize_model():
    inception_v3 = InceptionV3(include_top=False,
                               weights='imagenet',
                               input_tensor=None,
                               input_shape=(150, 150, 3),
                               pooling='avg')

    model = Sequential()
    model.add(inception_v3)
    model.add(Dense(units=1, activation='sigmoid'))
    model.compile(loss='binary_crossentropy',
                  optimizer='adam',
                  metrics=['accuracy'])

    model.save('cnn_model_test.h5')


def balance_data():
    count0 = 0
    count1 = 0

    hit_rows = []
    miss_rows = []

    with open(train_path) as csv_file:
        images_csv = csv.reader(csv_file)

        for row in images_csv:
            if row[3] == '1':
                count1 += 1
                hit_rows.append(row)
            else:
                count0 += 1
                miss_rows.append(row)

    hit_rows = random.sample(hit_rows, 15000)
    miss_rows = random.sample(miss_rows, 15000)

    all_data = miss_rows + hit_rows

    random.shuffle(all_data)

    with open('shuffled.csv', 'w') as writefile:
        writer = csv.writer(writefile)
        for row in all_data:
            writer.writerow(row)


def train_batch():
    start_time = time.time()
    batch_size = 32

    model = load_model('cnn_model_test.h5')

    # First row
    x_batch = []
    y_batch = []
    batch_count = 0

    print("Begin!")

    with open('shuffled.csv') as csv_file:
        images_csv = csv.reader(csv_file)
        for row in images_csv:
            try:
                img_mat = url2image(row[1])
                if img_mat.ndim != 3:
                    continue
            except:
                continue

            x_batch.append(img_mat)
            y_batch.append(row[3])

            if len(y_batch) == 32:
                x_train = np.stack(x_batch, axis=0)
                y_train = np.asarray(y_batch)

                # Load and train
                model.train_on_batch(x_train, y_train)
                model.save('cnn_model_test.h5')
                x_batch = []
                y_batch = []
                batch_count += 1
                print("Finished Batch " + str(batch_count) + " of " + str(math.ceil(30000/32)) +
                      " at " + time.strftime('%l:%M%p on %b %d, %Y'))

    print("Training took %s seconds." % (time.time() - start_time))


def url2image(url):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    img_resize = img.resize((150, 150), Image.ANTIALIAS)
    img_mat = np.array(img_resize)

    return img_mat


if __name__ == "__main__":
    initialize_model()
    train_batch()