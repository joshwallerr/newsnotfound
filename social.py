import json
import praw
import requests
from os import environ, path
from dotenv import load_dotenv
import os
import sys

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))

graph_url = 'https://graph.facebook.com/v16.0/'
ig_access_token = environ.get('IG_ACCESS_TOKEN')

if sys.argv[1] == 'uk' or sys.argv[1] == 'us' or sys.argv[1] == 'world' or sys.argv[1] == 'science':
    fb_id = environ.get('FACEBOOK_PAGE_ID')
    ig_id = environ.get('INSTAGRAM_ACCOUNT_ID')
    fb_access_token = environ.get('FB_ACCESS_TOKEN_NEWSNOTFOUND')
elif sys.argv[1] == 'teesside':
    fb_id = environ.get('FACEBOOK_PAGE_ID_TEESSIDE')
    ig_id = environ.get('INSTAGRAM_ACCOUNT_ID_TEESSIDE')
    fb_access_token = environ.get('FB_ACCESS_TOKEN_NEWSNOTFOUND_TEESSIDE')
else:
    raise Exception('Please specify a topic.')

print


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


# nnf_hl = headlines_links(['https://newsnotfound.com/'])
# three_headlines = list(nnf_hl.keys())[:3]
# print(three_headlines)
