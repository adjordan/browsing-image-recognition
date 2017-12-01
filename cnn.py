import scipy as sp
import numpy as np
import os
from keras.layers import Dense
from keras.applications.inception_v3 import InceptionV3


def main():
    inception_v3 = InceptionV3(include_top=False,
                               weights='imagenet',
                               input_tensor=None,
                               input_shape=(140, 140, 3),
                               pooling=None)

    inception_v3.add(Dense(unit=2, activation='sigmoid'))
    inception_v3.compile(loss='binary_crossentropy',
                         optimizer='rmsprop',
                         metrics=['accuracy'])

    inception_v3.fit(data, labels, epochs=10, batch_size=32)


def create_datasets():
    x_train = []
    y_train = []

    for image in os.listdir('img/r_pics'):
        img = sp.misc.imread(os.getcwd() + '/img/r_pics/'+image)

        x_train.append(img)
        y_train.append(1)



    x_train = np.asarray(x_train)
    y_train = np.asarray(y_train)
    return x_train, y_train


if __name__ == "__main__":
    x_train, y_train = create_datasets()
    print(x_train.shape)