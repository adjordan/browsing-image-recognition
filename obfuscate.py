import os
import base64
from string import ascii_letters, digits
from random import randint, choice

def gen_key():
    # Generate a random key and save to hidden file
    nchars = randint(1,256)
    key = ''.join(choice(ascii_letters + digits) for i in range(nchars))
    with open('.key', 'w') as f:
        f.write(key)

def get_key():
    # Load key from file
    with open('.key', 'r') as f:
        return f.read()

def to_string(filename, key):
    name = os.path.splitext(filename)[0]

    # Convert image binary to string
    with open(filename, 'rb') as f:
        im_str = base64.b64encode(f.read()).decode()

    # Add key to string and save as text
    with open('{}.enc'.format(name), 'wb') as f:
        f.write((key + im_str).encode())
    os.remove(filename)

def to_image(filename, key):
    name = os.path.splitext(filename)[0]

    # Load string and strip key
    with open(filename, 'rb') as f:
        im = f.read()
        im_str = im.decode()[len(key):]

    # Convert string to image binary
    with open('{}.jpg'.format(name), 'wb') as f:
        f.write(base64.b64decode(im_str))
    os.remove(filename)
