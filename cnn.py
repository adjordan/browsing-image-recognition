from keras.models import Sequential
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
    

if __name__ == "__main__":
    main()