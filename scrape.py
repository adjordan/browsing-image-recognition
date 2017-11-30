import os
import praw
import urllib.request


# Authentication so we can access reddit
def authenticate():
    print("Authenticating...")
    user_agent = praw.Reddit()
    print("Authenticated as {}".format(user_agent.user.me()))
    return user_agent


def download_images(dictionary):
    values = dictionary.values()
    keys = dictionary.keys()

    # Index through all keys (each key is a subreddit)
    for i in range(0, len(keys)):
        urls = values[i]

        # Create directory to save images if it doesn't exist
        save_dir = "r_" + keys[i]
        if not os.path.exists(save_dir):
            os.mkdir(save_dir)

        # Index through all images for the subreddit and save
        for j in range(0, len(urls)):
            url = urls[j]
            urllib.request.urlretrieve(url, save_dir + "/image_" + j)


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
