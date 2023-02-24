import json
import praw
import requests
from os import environ, path
from dotenv import load_dotenv
import os

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))

ig_id = environ.get('INSTAGRAM_ACCOUNT_ID')
igfb_access_token = environ.get('IGFB_ACCESS_TOKEN')
graph_url = 'https://graph.facebook.com/v16.0/'

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


def ig_post_image(caption, image_url, instagram_account_id=ig_id, access_token=igfb_access_token):
    url = graph_url + instagram_account_id + '/media'
    param = dict()
    param['access_token'] = access_token
    param['caption'] = caption
    param['image_url'] = image_url
    response = requests.post(url, params=param)
    response = response.json()
    
    # Publish container
    ig_publish_container(response['id'], instagram_account_id, access_token)


def ig_post_video(caption, video_url, instagram_account_id=ig_id, access_token=igfb_access_token):
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
def ig_publish_container(creation_id, instagram_account_id=ig_id, access_token=igfb_access_token):
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


def generate_ig_hashtags(topic):
    if topic == 'world':
        tags = '#worldnews #ainews #breakingnews #worldpolitics #worldnewstonight #internationalnews'
    elif topic == 'science':
        tags = '#science #sciencenews #ainews #scientistsofinstagram #sciencefacts'
    elif topic == 'uk':
        tags = '#uknews #newsuk #ukcountrynews #united_kingdom #ig_united_kingdom #ainews'
    elif topic == 'us':
        tags = '#usnews #usanews #united_states #ainews #conservativenews #democratnews'

    return tags 