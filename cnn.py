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
import scrape


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
model_path = "/home/austin/Github/browsing-image-recognition/cnn_model.h5"


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

    model.save(model_path)


def create_dataset():
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

    num_samples_per_class = count1
    hit_rows = random.sample(hit_rows, num_samples_per_class)
    miss_rows = random.sample(miss_rows, num_samples_per_class)

    all_data = miss_rows + hit_rows

    random.shuffle(all_data)

    with open('shuffled.csv', 'w') as writefile:
        writer = csv.writer(writefile)
        writer.writerow(['image_id', 'url', 'tags', 'label'])
        for row in all_data:
            writer.writerow(row)

    return num_samples_per_class * 2


def train_batch(num_samples):
    batch_size = 32
    model = load_model(model_path)

    # First row
    x_batch = []
    y_batch = []
    batch_count = 0

    start_time = time.time()
    print("Begin!")

    for img in scrape.get_images(filename='shuffled.csv', randomize=False):
        img_mat = img[0]
        label = img[1]
        if img_mat is None or img_mat.shape != (150, 150, 3):
            continue

        x_batch.append(img_mat)
        y_batch.append(label)

        if len(y_batch) == batch_size:
            x_train = np.stack(x_batch, axis=0)
            y_train = np.asarray(y_batch)

            # Load and train
            model.train_on_batch(x_train, y_train)
            model.save(model_path)
            x_batch = []
            y_batch = []
            batch_count += 1

            # print statements
            num_batches = math.ceil(num_samples / batch_size)
            avg_batch_time = (time.time() - start_time) / batch_count
            print("Finished Batch " + str(batch_count) + " of " + str(num_batches) +
                  " at " + time.strftime('%l:%M%p on %b %d, %Y') + ".")

            m, s = divmod(avg_batch_time * (num_batches - batch_count), 60)
            h, m = divmod(m, 60)
            h, m, s = int(h), int(m), round(s)
            print("Estimated time remaining: {:02d}h{:02d}m{:02d}s".format(h, m, s))
            print("\n")

    print("Training took %s seconds." % (time.time() - start_time))


# def url2image(url):
#     response = None
#     while response is None:
#         try:
#             response = requests.get(url, timeout=1)
#         except:
#             pass
#     img = Image.open(BytesIO(response.content))
#     img_resize = img.resize((150, 150), Image.ANTIALIAS)
#     img_mat = np.array(img_resize)
#
#     return img_mat


if __name__ == "__main__":
    initialize_model()
    num_samples = create_dataset()
    train_batch(num_samples)
