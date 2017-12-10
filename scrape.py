import os
import praw
import re
import obfuscate
import requests
import csv
import pandas as pd
from urllib import request, parse, error
from shutil import rmtree
import io
from PIL import Image

# Authentication so we can access reddit
def authenticate():
    print("Authenticating...")
    user_agent = praw.Reddit()
    print("Authenticated as {}".format(user_agent.user.me()))
    return user_agent


# Deletes all files in the 'img' directory
def clear_img_dir():
    rmtree('./img')
    os.makedirs('img')


# Tries to save a single image given a URL, subreddit, and file number
def save_image(url, key, image_id, hide=True):
    try:
        response = request.urlopen(url)
    except error.HTTPError as err:
        return
    img = Image.open(io.BytesIO(response.read()))
    img_resize = img.resize((150,150), Image.ANTIALIAS)

    if hide:
        byte_str = io.BytesIO()
        img_resize.save(byte_str, format='JPEG')
        obfuscate.stream_to_string(byte_str.getvalue(), key, image_id)
    else:
        img_resize.save('img/{}{}'.format(image_id, os.path.splitext(parse.urlparse(url)[2])[1]))

def lookup_url(image_id, filename='urls.csv'):
    df = pd.read_csv(filename, index_col='image_id')
    url, subreddit, valid = df.loc[image_id, :]
    print('{} ({})'.format(url, subreddit))


def download_images(filename='urls.csv', limit=100, hide=True, randomize=True):
    if not os.path.isfile('.key'):
        obfuscate.gen_key()
    key = obfuscate.get_key()

    # Read data from file and sample rows randomly
    if randomize:
        seed = None
    else:
        seed = 1
    df = pd.read_csv(filename, index_col='image_id')
    df = df.sample(limit, random_state=seed)

    # Attempt to download all images
    for image_id, (url, _, _) in df.iterrows():
        try:
            save_image(url, key, image_id, hide)
        except:
            pass


def validate_urls(filename='urls.csv'):
    # TODO make parsed url a dictionary
    # TODO check for bad status code before download

    valid_formats = ['jpeg', 'jpg', 'png', 'bmp', 'tiff']
    df = pd.read_csv(filename, index_col='image_id')
    df['valid'] = False
    for image_id, (url, subreddit, _) in df.iterrows():
        parsed = list(parse.urlparse(url))

        # Check for a file extension
        extension = os.path.splitext(parsed[2])[1]
        if extension:
            # Check for image formats
            if any(f in parsed[2] for f in valid_formats):
                df.loc[image_id, 'valid'] = True
        # Check for imgur links and force them to jpg domain
        else:
            if 'imgur' in parsed[1]:
                if '/a/' in parsed[2]: # skip albums
                    continue
                parsed[1] = 'i.imgur.com' # force domain to i.imgur.com
                parsed[2] += '.jpg' # add jpg file extension
                url = parse.urlunparse(parsed)
                df.loc[image_id, 'url'] = url
                df.loc[image_id, 'valid'] = True

    # Reset image ids to count from zero
    validated = df[df['valid']]
    validated = validated.reset_index(drop=True)
    validated.index.name = 'image_id'

    num_valid = len(validated)
    total = len(df)
    print('{:,} ({:.0%}) of {:,} urls are valid.'.format(num_valid, num_valid/total, total))
    validated.to_csv('urls.csv')


def scrape_all(min_score, filename='urls.csv'):

    user_agent = authenticate()

    # Get subreddits from file
    with open('subreddits.txt', 'r') as f:
        subreddits = f.readlines()
    subreddits = [x.strip() for x in subreddits]
    num_subs = len(subreddits)

    # Loop through all subreddits in the text file
    urls = []
    print('Scraping {} subreddits for posts with at least {} score...' \
        .format(num_subs, min_score), end=' ')
    for i, s in enumerate(subreddits):
        print(i+1, end=' ')
        subreddit = user_agent.subreddit(s)

        # Loop through top posts in the subreddit
        submissions = subreddit.top(limit=None)
        for submission in submissions:
            # Append URL to dictionary if above threshold
            if submission.score >= min_score:
                urls.append([submission.url, s])
    print('Done!')

    df = pd.DataFrame(urls, columns=['subreddit', 'url'])
    df.index.name = 'image_id'
    df.to_csv(filename)

    print('Scraped and saved {:,} urls.'.format(len(urls)))


if __name__ == '__main__':
    subreddit_dict = scrape_all()
    download_images(subreddit_dict)
