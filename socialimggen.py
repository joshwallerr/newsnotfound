import textwrap
from PIL import Image, ImageDraw, ImageFont
import requests
from bs4 import BeautifulSoup
from scrape import scrape_articles
import random
import sys
from scrape import get_article_images
from imgurpython import ImgurClient
from os import environ, path
from dotenv import load_dotenv
from social import ig_post_image, fb_post_image
import tweepy
import os

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))

if len(sys.argv) != 2:
    raise Exception('Please provide cmd line param')


def scrape_rss_feeds(feeds):
    headlines = []
    for feed in feeds:
        r = requests.get(feed)
        soup = BeautifulSoup(r.content, features='xml')

        for item in soup.findAll('item'):
            if len(item.find_all('category')) != 1 and item.find('category').text.lower() not in ['world', 'united kingdom', 'united states', 'science', 'technology', 'teesside news']:
                print('skipping')
                continue

            if item.find('category').text.lower() not in ['world', 'united kingdom', 'united states', 'science', 'technology', 'teesside news']:
                # print()
                continue

            headline = item.find('title').text
            link = item.find('link').text
            get_cover_image([link])
            summary = f"{get_oss(link)}\n\nFull story: {link}"

            headlines.append(headline)
            break

    return headlines, summary

def get_oss(url):
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(response.text, 'html.parser')

    summary = ""
    article_div = soup.find('div', class_='entry-content')
    for p in article_div.find_all('p'):
        text = p.get_text()
        summary += text
        break

    # remove "One sentence summary - " from the start of the summary
    summary = summary[23:]

    return summary

def get_cover_image(link):
    images = get_article_images(link)
    print(images)
    
    # download image and save to images/fullscrnimage.png
    r = requests.get(images[0], allow_redirects=True)
    open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images/fullscrnimage.png'), 'wb').write(r.content)

def choose_social_article():
    # Determine feeds to use based on cmd line params
    if sys.argv[1] == 'uk':
        feeds = ["https://newsnotfound.com/united-kingdom/feed"]
        category = ['united kingdom']
    elif sys.argv[1] == 'tech':
        feeds = ["https://newsnotfound.com/science-tech/feed/"]
        category = ['science & technology']
    elif sys.argv[1] == 'world':
        feeds = ["https://newsnotfound.com/world/feed/"]
        category = ['world']
    elif sys.argv[1] == 'us':
        feeds = ["https://newsnotfound.com/united-states/feed"]
        category = ['united states']
    elif sys.argv[1] == 'teesside':
        feeds = ["https://newsnotfound.com/united-kingdom/regions-uk/teesside-news/feed/"]
        category = ['teesside']
    else:
        raise Exception('Invalid cmd line param')

    headlines, summary = scrape_rss_feeds(feeds)
    combined_list = list(zip(headlines, category))
    return combined_list, summary

def create_social_image(category, headline):
    # Open the background image
    background = Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images/fullscrnimage.png'))

    # Ensure the image is in RGBA mode
    background = background.convert("RGBA")

    # Resize to 1080 x 1080
    background = background.resize((1080, 1080))

    # Create a new transparent image for the gradient
    gradient = Image.new("RGBA", background.size)

    # Create a draw object
    draw = ImageDraw.Draw(gradient)

    # Create a black gradient
    for i in range(1080, 360, -1):
        color = int(255 * ((1080 - i) / 720))  # Gradient step
        draw.line([(0, i), (1080, i)], fill=(0, 0, 0, 255 - color))

    # Combine the gradient and background
    background = Image.alpha_composite(background, gradient)

    # Draw the white line
    draw = ImageDraw.Draw(background)
    draw.line([(50, 770), (1030, 770)], fill="white", width=3)  # Made line longer

    # Open the font
    font_big = ImageFont.truetype(os.path.join(os.path.dirname(os.path.abspath(__file__)), "Ubuntu-Bold.ttf"), int(45 * 1.55))  # Increased size by 55% (35% + 20%)
    font_small = ImageFont.truetype(os.path.join(os.path.dirname(os.path.abspath(__file__)), "Ubuntu-Medium.ttf"), int(35 * 1.3))  # Increased size by 30% (20% + 10%)

    # Draw the headline text
    text = f"{headline}"
    lines = textwrap.wrap(text, width=24)  # Adjust width as needed
    y_text = 780  # Moved up
    for line in lines:
        width, height = draw.textbbox((0,0), line, font=font_big)[2:]
        draw.text(((1080 - width) / 2, y_text), line, font=font_big, fill="white")
        y_text += height

    # Draw the category text
    text = f"{category}"
    text_width, text_height = draw.textbbox((0,0), text, font=font_small)[2:]
    draw.text(((1080 - text_width) / 2, 720 - text_height / 2), text, fill="white", font=font_small)

    # Add the logo
    logo = Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "images/sqrlogo.png"))
    logo = logo.resize((56, 56))
    background.paste(logo, (1024, 1024), logo)

    # Save the image
    background.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), "images/newsimage.png"))

text_data, summary = choose_social_article()
print(text_data)

headline, category = text_data[0]

# make headlines and category uppercase
headline = headline.upper()
category = category.upper()

# make sure headline is less than 121 characters
if len(headline) > 120:
    raise Exception('Headline too long')

create_social_image(category, headline)

imgur_client_id = environ.get('IMGUR_CLIENT_ID')
imgur_client_secret = environ.get('IMGUR_CLIENT_SECRET')
image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images/newsimage.png')

def upload_image_to_imgur(client_id, client_secret, image_path):
    client = ImgurClient(client_id, client_secret)
    response = client.upload_from_path(image_path)
    return response['link']

image_url = upload_image_to_imgur(imgur_client_id, imgur_client_secret, image_path)
print(image_url)

def get_twitter_conn_v1():
    auth = tweepy.OAuth1UserHandler(environ.get('TWITTER_API_KEY'), environ.get('TWITTER_API_SECRET_KEY'))
    auth.set_access_token(
        environ.get('TWITTER_ACCESS_TOKEN'),
        environ.get('TWITTER_ACCESS_TOKEN_SECRET'),
    )
    return tweepy.API(auth)

def get_twitter_conn_v2():
    client = tweepy.Client(
        consumer_key = environ.get('TWITTER_API_KEY'),
        consumer_secret = environ.get('TWITTER_API_SECRET_KEY'),
        access_token = environ.get('TWITTER_ACCESS_TOKEN'),
        access_token_secret = environ.get('TWITTER_ACCESS_TOKEN_SECRET'),
    )

    return client

# caption_ig = summary without the "Full story: link" part
caption_ig = summary.split('Full story:')[0]
caption = summary
caption_twitter = summary

if len(caption_twitter) > 280:
    caption_twitter = caption_twitter.split('Full story:')[0]
    if len(caption_twitter) > 280:
        caption_twitter = caption_twitter[:277] + '...'

# print(caption_ig)
# print(caption_fb)

if category != 'TEESSIDE':
    ig_post_image(caption_ig, image_url)
    fb_post_image(caption, image_url)


client_v1 = get_twitter_conn_v1()
client_v2 = get_twitter_conn_v2()

media_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images/newsimage.png")
media = client_v1.media_upload(filename=media_path)
media_id = media.media_id

client_v2.create_tweet(text=f"{caption_twitter}", media_ids=[media_id])
