import os
import praw
import re
import obfuscate
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
def save_image(url, key, subreddit, file_number, hide=True):
    try:
        response = request.urlopen(url)
    except error.HTTPError as err:
        return
    img = Image.open(io.BytesIO(response.read()))
    img_resize = img.resize((150,150), Image.ANTIALIAS)

    if hide:
        byte_str = io.BytesIO()
        img_resize.save(byte_str, format='JPEG')
        obfuscate.stream_to_string(byte_str.getvalue(), key, subreddit, file_number)
    else:
        img_resize.save('img/r_{}/{}_{}.jpg'.format(subreddit, subreddit, file_number))


# Downloads the top N images from a subreddit
def download_images(urls, hide=True):
    if not os.path.isfile('.key'):
        obfuscate.gen_key()
    key = obfuscate.get_key()

    for subreddit, sub_urls in urls.items():
        save_dir = 'img/r_' + subreddit
        os.makedirs(save_dir, exist_ok=True)

        for i, url in enumerate(sub_urls):
            parsed = list(parse.urlparse(url))
            # Check to see if URL is already in image file format
            if re.match('.*\.(?:jpeg|jpg|png|bmp|tiff|gif)$', parsed[2]):
                save_image(url, key, subreddit, i+1, hide)
            # Adjust imgur URL format to point to the image file, skipping albums
            elif 'imgur' in parsed[1]:
                if '/a/' in parsed[2]: # skip albums
                    continue
                parsed[1] = 'i.imgur.com' # force domain to i.imgur.com
                parsed[2] += '.jpg' # add jpg file extension
                url = parse.urlunparse(parsed)
                save_image(url, key, subreddit, i+1, hide)

def scrape_all():
    user_agent = authenticate()

    temp = open('subreddits.txt', 'r')
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
