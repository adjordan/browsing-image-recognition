import scipy as sp
import numpy as np
import os
from keras.layers import Dense
from keras.models import Sequential
from keras.applications.inception_v3 import InceptionV3


def build_cnn():
    inception_v3 = InceptionV3(include_top=False,
                               weights='imagenet',
                               input_tensor=None,
                               input_shape=(140, 140, 3),
                               pooling=None)

    model = Sequential()
    model.add(inception_v3)
    model.add(Dense(units=2, activation='sigmoid'))
    model.compile(loss='binary_crossentropy',
                  optimizer='rmsprop',
                  metrics=['accuracy'])

    #inception_v3.fit(data, labels, epochs=10, batch_size=32)

    return model


def create_datasets():
    x_train = []
    y_train = []
    x_test = []
    y_test = []

    num_false = len([f for f in os.listdir('img/r_pics')])
    num_true = len([f for f in os.listdir('img/r_catsstandingup')])

    perc = 0.8
    thresh_true = round(num_true * perc)
    thresh_false = round(num_false * perc)

    for i, image in enumerate(os.listdir('img/r_pics')):
        img = sp.misc.imread(os.getcwd() + '/img/r_pics/'+image)

        if i < thresh_false:
            x_train.append(img)
            y_train.append(0)
        else:
            x_test.append(img)
            y_test.append(0)

    for i, image in enumerate(os.listdir('img/r_catsstandingup')):
        img = sp.misc.imread(os.getcwd() + '/img/r_catsstandingup/'+image)

        if i < thresh_true:
            x_train.append(img)
            y_train.append(1)
        else:
            x_test.append(img)
            y_test.append(1)

    x_train = np.asarray(x_train)
    y_train = np.asarray(y_train)
    return x_train, y_train


if __name__ == "__main__":

    #model = build_cnn()
    x_train, y_train = create_datasets()
    print(x_train.shape)