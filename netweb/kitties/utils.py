from keras.models import load_model
from PIL import Image
import requests
from io import BytesIO
import os

import tensorflow as tf
import numpy as np

local = os.path.dirname(os.path.abspath(__file__))
h5_file = os.path.join(local, 'cnn_model.h5')
model = load_model(h5_file)
graph = tf.get_default_graph()


def predict(url):
    global graph
    with graph.as_default():
        response = requests.get(url, timeout=3)
        img = Image.open(BytesIO(response.content))
        img_resize = img.resize((150, 150), Image.ANTIALIAS)
        img_mat = np.array(img_resize)
        model_input = np.expand_dims(img_mat, axis=0)
        result = model.predict(model_input)

        return result > 0.5
