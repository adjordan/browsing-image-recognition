import os
import praw
import urllib.request

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
def save_image(url, subreddit, file_number):
    try:
        urlretrieve(url, 'img/r_{}/{}.jpg'.format(subreddit, file_number))
    except:
        pass

# Downloads the top N images from a subreddit
def download_images(subreddit, limit):
    os.makedirs('img/r_{}'.format(subreddit), exist_ok=True)
    for i, post in enumerate(subreddit.top(limit=limit)):
        url = post.url
        # Check to see if URL is already in image file format
        if re.match('.*\.(?:jpeg|jpg|png|bmp|tiff|gif)$', url):
            save_image(url, subreddit, i)
        # Adjust imgur URL format to point to the image file, skipping albums
        elif 'imgur' in post.domain:
            parsed = list(urlparse(url))
            if re.match('/a/.*', parsed[2]): # skip albums
                continue
            if parsed[1] != 'i.imgur.com': # use image hosting domain
                parsed[1] = 'i.imgur.com'
            if not re.match('.*\.(?:jpeg|jpg|png|bmp|tiff|gif)$', parsed[2]): # add jpg file extension
                parsed[2] += '.jpg'
                url = urlunparse(parsed)
            save_image(url, subreddit, i+1)

def scrape():
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
    scrape()
