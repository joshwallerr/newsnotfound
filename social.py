import json
import praw
import requests
import os

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
