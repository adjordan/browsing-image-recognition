from PIL import Image
import requests
from io import BytesIO
import numpy as np


def predict_url(model, url):
    response = requests.get(url, timeout=3)
    img = Image.open(BytesIO(response.content))
    img_resize = img.resize((150, 150), Image.ANTIALIAS)
    img_mat = np.array(img_resize)
    model_input = np.expand_dims(img_mat, axis=0)
    result = model.predict(model_input)

    if result > 0.5:
        print("This is a cat!")
    else:
        print("This is not a cat.")
