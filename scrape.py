import os
import praw
import re
from urllib.request import urlretrieve
from urllib.parse import urlparse, urlunparse
from shutil import rmtree

from PIL import Image
import urllib.request
import cv2


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
# def save_image(url, subreddit, file_number):
#     try:
#         urlretrieve(url, 'img/r_{}/{}_image_{}.jpg'.format(subreddit, subreddit, file_number))
#     except:
#         pass


def save_image(url, subreddit, file_number):
    try:
        with urllib.request.urlopen(url) as url:
            with open('temp.jpg', 'wb') as f:
                f.write(url.read())

        img = Image.open('temp.jpg')
        img_resize = img.resize((150,150), Image.ANTIALIAS)
        img_resize.save('img/r_{}/{}_image_{}.jpg'.format(subreddit, subreddit, file_number))
    except urllib.error.HTTPError as err:
        pass


# Downloads the top N images from a subreddit
# def download_images(subreddit, limit):
#     os.makedirs('img/r_{}'.format(subreddit), exist_ok=True)
#     for i, post in enumerate(subreddit.top(limit=limit)):
#         url = post.url
#         # Check to see if URL is already in image file format
#         if re.match('.*\.(?:jpeg|jpg|png|bmp|tiff|gif|gifv)$', url):
#             save_image(url, subreddit, i)
#         # Adjust imgur URL format to point to the image file, skipping albums
#         elif 'imgur' in post.domain:
#             parsed = list(urlparse(url))
#             if re.match('/a/.*', parsed[2]): # skip albums
#                 continue
#             parsed[1] = 'i.imgur.com' # force domain to i.imgur.com
#             parsed[2] += '.jpg' # add jpg file extension
#             url = urlunparse(parsed)
#             save_image(url, subreddit, i+1)


def download_images(subreddit_dict):
    for key in subreddit_dict:
        urls = subreddit_dict[key]
        save_dir = 'img/r_' + key

        # Create directory for subreddit if it doesnt exist
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        # Parse urls
        i = 1
        for url in urls:
            if re.match('.*\.(?:jpeg|jpg|png|bmp|tiff)$', url):
                save_image(url, key, i)
                i += 1
            # Adjust imgur URL format to point to the image file, skipping albums
            elif 'imgur' in url:
                if '/a/' in url:  # skip albums
                    continue
                parsed = list(urlparse(url))
                parsed[1] = 'i.imgur.com'  # force domain to i.imgur.com
                parsed[2] += '.jpg'  # add jpg file extension
                url = urlunparse(parsed)
                save_image(url, key, i)
                i += 1

def scrape_all():
    user_agent = authenticate()

    temp = open("subreddits.txt", "r")
    subreddits = temp.readlines()
    subreddits = [x.strip() for x in subreddits]

    out_dict = {}

    # Loop through all subreddits in the text file
    for s in subreddits:
        out_dict[s] = []
        subreddit = user_agent.subreddit(s)

        # Loop through top posts in the subreddit
        for submission in subreddit.top(limit=10):
            # Append URL to dictionary
            # TODO: Only take URLs from specific sites
            # TODO: Get direct image from Imgur links
            # TODO: Get individual pictures from Imgur albums
            out_dict[s].append(submission.url)

    return out_dict


if __name__ == '__main__':
    subreddit_dict = scrape_all()
    download_images(subreddit_dict)