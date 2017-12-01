import os
import praw
import re
import obfuscate
from urllib.request import urlopen
from urllib.parse import urlparse, urlunparse
from shutil import rmtree

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
def save_image(url, key, subreddit, file_number):
    try:
        response = urlopen(url)
        obfuscate.stream_to_string(response.read(), key, subreddit, file_number)
    except:
        pass

# Downloads the top N images from a subreddit
def download_images(subreddit, limit):
    if not os.path.isfile('.key'):
        obfuscate.gen_key()
    key = obfuscate.get_key()
    os.makedirs('img/r_{}'.format(subreddit), exist_ok=True)
    for i, post in enumerate(subreddit.top(limit=limit)):
        url = post.url
        # Check to see if URL is already in image file format
        if re.match('.*\.(?:jpeg|jpg|png|bmp|tiff|gif)$', url):
            save_image(url, key, subreddit, i)
        # Adjust imgur URL format to point to the image file, skipping albums
        elif 'imgur' in post.domain:
            parsed = list(urlparse(url))
            if re.match('/a/.*', parsed[2]): # skip albums
                continue
            parsed[1] = 'i.imgur.com' # force domain to i.imgur.com
            parsed[2] += '.jpg' # add jpg file extension
            url = urlunparse(parsed)
            save_image(url, key, subreddit, i+1)

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
        for submission in subreddit.top(limit=2000):
            # Append URL to dictionary
            # TODO: Only take URLs from specific sites
            # TODO: Get direct image from Imgur links
            # TODO: Get individual pictures from Imgur albums
            out_dict[s].append(submission.url)

    return out_dict

if __name__ == '__main__':
    scrape_all()
