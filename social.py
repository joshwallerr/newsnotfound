import json
import praw
import requests
from os import environ, path
from dotenv import load_dotenv
import os
import sys
import sqlite3
import random
import csv

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))

graph_url = 'https://graph.facebook.com/v16.0/'
ig_access_token = environ.get('IG_ACCESS_TOKEN')


if len(sys.argv) > 1:
    if sys.argv[1] == 'teesside':
        fb_id = environ.get('FACEBOOK_PAGE_ID_TEESSIDE')
        ig_id = environ.get('INSTAGRAM_ACCOUNT_ID_TEESSIDE')
        fb_access_token = environ.get('FB_ACCESS_TOKEN_NEWSNOTFOUND_TEESSIDE')
    else:
        fb_id = environ.get('FACEBOOK_PAGE_ID')
        ig_id = environ.get('INSTAGRAM_ACCOUNT_ID')
        fb_access_token = environ.get('FB_ACCESS_TOKEN_NEWSNOTFOUND')
else:
    fb_id = environ.get('FACEBOOK_PAGE_ID')
    ig_id = environ.get('INSTAGRAM_ACCOUNT_ID')
    fb_access_token = environ.get('FB_ACCESS_TOKEN_NEWSNOTFOUND')


def reddit_post(title, slug):
    subr = 'newsnotfound'
    credentials = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'client_secrets.json')
    
    with open(credentials) as f:
        creds = json.load(f)
    
    reddit = praw.Reddit(client_id=creds['client_id'],
                        client_secret=creds['client_secret'],
                        user_agent=creds['user_agent'],
                        redirect_uri=creds['redirect_uri'],
                        refresh_token=creds['refresh_token'])
    
    subreddit = reddit.subreddit(subr)
    
    title = title + ' | NewsNotFound'

    url = 'https://newsnotfound.com/' + slug
    
    subreddit.submit(title, url=url)


def ig_post_image(caption, image_url, instagram_account_id=ig_id, access_token=ig_access_token):
    url = graph_url + instagram_account_id + '/media'
    param = dict()
    param['access_token'] = access_token
    param['caption'] = caption
    param['image_url'] = image_url
    response = requests.post(url, params=param)
    response = response.json()
    print(response)
    
    # Publish container
    ig_publish_container(response['id'], instagram_account_id, access_token)


def fb_post_image(caption, image_url, facebook_account_id=fb_id, access_token=fb_access_token):
    image_post_url = 'https://graph.facebook.com/{}/photos'.format(facebook_account_id)
    
    payload = {
        'message': caption,
        'url': image_url,
        'access_token': access_token
    }

    #Send the POST request
    response = requests.post(image_post_url, data=payload)
    # print(response.text)


def ig_post_video(caption, video_url, instagram_account_id=ig_id, access_token=ig_access_token):
    url = graph_url + instagram_account_id + '/media'
    param = dict()
    param['access_token'] = access_token
    param['caption'] = caption
    param['video_url'] = video_url
    param['media_type'] = 'VIDEO'
    param['thumb_offset'] = '10'
    response = requests.post(url, params=param)
    response = response.json()
    
    # Publish container
    ig_publish_container(response['id'], instagram_account_id, access_token)


# creation_id is container_id
def ig_publish_container(creation_id, instagram_account_id=ig_id, access_token=ig_access_token):
    url = graph_url + instagram_account_id + '/media_publish'
    param = dict()
    param['access_token'] = access_token
    param['creation_id'] = creation_id
    response = requests.post(url,params=param)
    response = response.json()
    # print(response)


def generate_ig_caption(excerpt, hashtags):
    caption = excerpt + '\n\n' + hashtags
    return caption


def generate_fb_caption(excerpt, slug):
    url = 'https://newsnotfound.com/' + slug
    caption = excerpt + '\n\n' + 'Read the full story on our website: ' + url
    return caption


def generate_ig_hashtags(topic):
    if topic == 'world':
        tags = '#worldnews #ainews #breakingnews #worldpolitics #worldnewstonight #internationalnews'
    elif topic == 'science':
        tags = '#science #sciencenews #ainews #scientistsofinstagram #sciencefacts'
    elif topic == 'uk':
        tags = '#uknews #newsuk #ukcountrynews #united_kingdom #ig_united_kingdom #ainews'
    elif topic == 'us':
        tags = '#usnews #usanews #united_states #ainews #conservativenews #democratnews'
    elif topic == 'teesside':
        tags = '#teessidenews #boro #middlesbrough #northeast #teesside'

    return tags 


def generate_tiktok_video(story1, story2, story3, funny_story, image_url1, image_url2):
    elai_api_key = environ.get('ELAI_API_KEY')
    url = "https://apis.elai.io/api/v1/videos/renderTemplate/63fa2cd8912ad050602ece2f"

    print(image_url1)
    print(image_url2)

    payload = {
        "templateData": [
            {
                "story1": story1,  # Start story 1
                "canvastxt1": story1,
                "929527292291": image_url1,  # 1st Image URL here
                "story2": story2,  # Start story 2
                "canvastxt2": story2,
                "story3": story3,  # Start story 3
                "canvastxt3": story3,
                "515125141627": image_url2,  # 2nd Image URL here
                "funnystory": funny_story,
            },
        ],
        "emailNotification": True,
        "fitTextBox": True
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": "Bearer " + elai_api_key
    }

    response = requests.post(url, json=payload, headers=headers)

    print(response.text)
    return response.text


def load_tiktok_data():
    # Connect to the database
    conn = sqlite3.connect(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tiktok', 'tiktok.db'))
    c = conn.cursor()

    # Create the table if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS tiktok
                (id INTEGER PRIMARY KEY AUTOINCREMENT, stories TEXT, captions TEXT, used INTEGER DEFAULT 0)''')

    # Open the CSV file and read the data
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tiktok', 'tiktok.csv'), newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Insert the row into the table
            c.execute("INSERT INTO tiktok (stories, captions) VALUES (?, ?)", (row['stories'], row['captions']))
            
    # Commit the changes and close the connection
    conn.commit()
    conn.close()


def get_tiktok_story_caption():
    # Connect to the database
    conn = sqlite3.connect(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tiktok', 'tiktok.db'))
    c = conn.cursor()

    # Select a random row where used=0
    c.execute("SELECT * FROM tiktok WHERE used=0 ORDER BY RANDOM() LIMIT 1")

    # Fetch the data and store it in variables
    data = c.fetchone()
    if data is not None:
        id_, funny_story, tiktok_caption, _ = data
        # Update the row to set used=1
        c.execute("UPDATE tiktok SET used=1 WHERE id=?", (id_,))
        conn.commit()
    else:
        # No unused rows found
        funny_story = ''
        tiktok_caption = ''

    # Close the database connection
    conn.close()

    return funny_story, tiktok_caption


def retrieve_tiktok_video(video_id):
    # Get video URL
    elai_api_key = environ.get('ELAI_API_KEY')
    url = f"https://apis.elai.io/api/v1/videos/{video_id}"

    headers = {
        "accept": "application/json",
        "Authorization": "Bearer " + elai_api_key
    }

    response = requests.get(url, headers=headers)

    print(response.text)
    return response.text


def download_tiktok_video(video_url):
    response = requests.get(url)

    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'videos', 'video.mp4'), 'wb') as f:
        f.write(response.content)


# nnf_hl = headlines_links(['https://newsnotfound.com/'])
# three_headlines = list(nnf_hl.keys())[:3]
# print(three_headlines)
