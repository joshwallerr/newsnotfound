# Cron set to run this script every 6 hours

from scrape import headlines_links, scrape_articles
import openai
from os import environ, path
from dotenv import load_dotenv
import ast
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import csv
import datetime
import os
import re
from textblob import TextBlob
import base64
import requests
import io
from PIL import Image
from stability_sdk import client
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
import json
import sys
from social import reddit_post

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))

api_key = environ.get('OPENAI_API_KEY') 
openai.api_key = api_key

wordpress_user = environ.get('WP_USER')
wordpress_password = environ.get('WP_APP_PWORD')
wordpress_credentials = wordpress_user + ":" + wordpress_password
wordpress_token = base64.b64encode(wordpress_credentials.encode())
wordpress_header = {'Authorization': 'Basic ' + wordpress_token.decode('utf-8')}


def main():
    create_covered_csv()

    # print(sys.argv[1])
    urls = get_urls(sys.argv[1])

    all_headlines_links = headlines_links(urls)

    all_headlines = all_headlines_links.keys()
    print(all_headlines)

    # Choose most relavent headlines
    story_headlines = get_story(escape_quotes(all_headlines))
    # # print('\n')
    print(story_headlines)

    # Check relavence of chosen headlines
    story_headlines = check_relevance(story_headlines)
    print('RELAVENT HEADLINES')
    print(story_headlines)

    # Scrape articles
    scraped_articles = scrape_articles(unescape_quotes(story_headlines), all_headlines_links)
    # print(scraped_articles)

    # Choose longest article from list of scraped articles
    scraped_article = choose_longest(scraped_articles)
    print(scraped_article)

    # Get points
    story_points = get_points(scraped_article)
    # print(story_points)

    # Generate article
    article = generate_article(story_points)
    # print(article)

    print('--------------- ARTICLE SEPARATOR ------------------')

    # Check for, and remove bias
    article = bias_checker(article)
    print(article)

    # Formatting to start a new line after every sentence
    article = format_article(article)
    print('--------------- ARTICLE SEPARATOR ------------------')
    print(article)

    # Generate headline
    article_headline = generate_headline(article)
    # print(article_headline)

    # Prevent default output - temporary bug fix
    if 'WHO Study Links Air Pollution to Increased' in article_headline:
        raise Exception('Default article generated. Failed run.')

    # Generate excerpt
    article_excerpt = generate_excerpt(article)
    print(article_excerpt)

    # Generate slug
    article_slug = generate_slug(article_headline)
    # print(article_slug)

    # Convert article to html
    html_article = html_converter(article)
    # print(html_article)

    # Generate html list
    html_list = generate_html_list(html_article)
    # print(html_list)

    # Combine and prepare article content
    html_content = f'<h3 class=\"title_seps\">At a glance</h3>{html_list}<h3 class=\"title_seps\">The details</h3>{html_article}'

    # Get categories
    category_ids = get_categories(sys.argv[1])

    # Generate post image and get id
    generate_image(article_headline)
    featured_media_id = upload_image()

    # Create Wordpress post
    response_code = create_wordpress_post(html_content, article_headline, article_excerpt, article_slug, category_ids, featured_media_id)
    print(response_code)

    # if 200 <= response_code.status_code <= 299:
    if response_code.ok:
        # Mark chosen headlines as covered
        mark_covered(unescape_quotes(story_headlines))
        print('Successfully pushed post to Wordpress!')
    else:
        raise Exception('Could not push to Wordpress')
    
    # Post on subreddit
    reddit_post(article_headline, article_slug)

    # Post on Instagram


def get_urls(topic):
    topic = topic.lower()
    if topic == 'world':
        urls = [
            'https://www.reuters.com/world/'
            'https://www.telegraph.co.uk/world-news/',
            'https://apnews.com/hub/world-news',
            'https://www.washingtonpost.com/world/',
            'https://news.sky.com/world',
            'https://www.bbc.co.uk/news/world'
        ]
    elif topic == 'science':
        urls = [
            'https://www.bbc.co.uk/news/science_and_environment'
            'https://www.theguardian.com/science',
            'https://www.independent.co.uk/news/science',
            'https://www.newscientist.com/section/news/',
            'https://scitechdaily.com/news/science/'
        ]
    elif topic == 'uk':
        urls = [
            'https://www.bbc.co.uk/news/uk'
            'https://www.reuters.com/world/uk/',
            'https://www.theguardian.com/uk-news',
            'https://news.sky.com/uk',
            'https://www.independent.co.uk/news/uk'
        ]
    elif topic == 'us':
        urls = [
            'https://www.theguardian.com/us-news'
            'https://www.reuters.com/world/us/',
            'https://www.bbc.co.uk/news/world/us_and_canada',
            'https://eu.usatoday.com/news/',
            'https://www.independent.co.uk/news/world/americas'
        ]
    else:
        raise Exception('Please provide one of the following arguments: world, science, tech, business, uk, us')

    return urls


def get_story(headlines):
    prompt = (f"Find as many headlines as you can from the below list of news headlines, that are about the exact same story. Output the related headlines in a python list format, where each list item is a list of contextually matched headlines, with no other text above or below. Only include stories that have at least 2 other headlines associated with them. The outputted list cannot have more than 3 items in it, so choose the headlines that you include in the list wisely.\n\n{headlines}")

    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=1000,
            temperature=0.1,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        related_headlines = response["choices"][0]["text"]
        related_headlines = related_headlines.replace("', '", "^!!").replace("['", "^^!").replace("'], ", "^^^").replace("']]", "^!^").replace("'", "\\'").replace('"', '\\"').replace('‘', '\\‘').replace('’', '\\’').replace(',', '\\,').replace("^!!", "', '").replace("^^!", "['").replace("^^^", "'], ").replace("^!^", "']]")
        related_headlines = ast.literal_eval(related_headlines)
    except: 
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=1000,
            temperature=0,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        related_headlines = response["choices"][0]["text"]
        related_headlines = related_headlines.replace("\\'", "\'")
        # print(related_headlines)
        related_headlines = ast.literal_eval(related_headlines)

    for headlines in related_headlines:
        if check_covered(unescape_quotes(headlines)) == False:
            chosen_story_headlines = headlines
            break
        else:
            chosen_story_headlines = None
            continue

    if chosen_story_headlines is not None:
        return chosen_story_headlines
    else:
        raise Exception('All stories covered')


def choose_longest(articles):
    longest = 0
    longest_article = ['']
    for article in articles:
        if len(article) > longest:
            longest = len(article)
            longest_article[0] = article

    return longest_article


def get_points(articles):
    points = []
    for article in articles:
        if len(article) <= 10:
            # print('Passing article')
            continue

        prompt = f'Based on the following article, please create as many bullet points as you can about all of the information. Please keep the bullet points as neutral and unbiased as possible, and feel free to change the wording of things (except quotes) to remove any biased tones and language - stick to neutral facts only. Please only output the bulleted list, nothing else. \n\n{article}'
        
        while(True):
            try:
                response = openai.Completion.create(
                    engine="text-davinci-003",
                    prompt=prompt,
                    max_tokens=1000,
                    temperature=0,
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0
                )
                points.append(response["choices"][0]["text"])
                break
            except:
                sentences = re.split(r'[.!?]', article, maxsplit=1)
                article = ' '.join(sentences[:-1])
                prompt = (f"Based on the following article, please create as many bullet points as you can about all of the information. Please keep the bullet points as neutral and unbiased as possible, and feel free to change the wording of things (except quotes) to remove any biased tones and language - stick to neutral facts only. Please only output the bulleted list, nothing else. \n\n{article}")
    return points


def generate_article(points):
    prompt = (f"Based on the below points, please generate me a whole news article for use on a news company's website. The article must be completely unbiased and wrote from a neutral point of view. Please make the article as long and detailed as possible, with as much information as you can fit. Please write in the inverted pyramid format, and lay the content out so that each sentence is its own paragraph. Please also try to ensure no more than 25% of sentences contain more than 20 words:\n\n{points}")
    
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=2042,
        temperature=0,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    article = response["choices"][0]["text"]
    return article


def bias_checker(article):
    bias_rating = calculate_bias(article)
    print(bias_rating)

    recursive_count = 0
    while bias_rating != 5:
        if recursive_count == 3:
            # if bias_rating == 4 or bias_rating == 6:
            #     return new_article
            # else:
            raise Exception('Reached max recursions. Could not remove bias.')

        para_list = article.split("\n")
        para_list = [item.strip() for item in para_list if item.strip() != ""]

        new_paras = []
        for para in para_list:
            prompt = (f"Please look at the below paragraph from a news article and reword any instances of bias, whether positive or negative, so that the whole paragraph is completely unbiased and doesn't push any particular narrative - the purpose is to inform readers, not push an opinion:\n\n{para}")
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                max_tokens=500,
                temperature=0,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
            )
            new_paras.append(response["choices"][0]["text"])
        print(new_paras)
        article = " ".join(new_paras)
        recursive_count += 1
        bias_rating = calculate_bias(article)
        print(bias_rating)

    print('Passed bias test')
    return article

def generate_headline(article):
    prompt = (f"Please generate me a short, unbiased headline for the below news article. The headlines must not contain more than 65 characters. Please just output the headline: {article}")
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=1000,
        temperature=0.1,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    article_headline = response["choices"][0]["text"]

    if article_headline == '':
        raise Exception('Failed to generate headline.')

    # print(article_headline)
    return article_headline


def generate_excerpt(article):
    prompt = (f"Please generate me a short, unbiased excerpt for the below news article. The excerpt should be relatively short, and no more than one sentence long. Please just output the excerpt: {article}")
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=1000,
        temperature=0.1,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    article_excerpt = response["choices"][0]["text"]

    if article_excerpt == '':
        raise Exception('Failed to generate headline.')

    # print(article_excerpt)
    return article_excerpt


def generate_slug(headline):
    slug = headline
    slug = re.sub(r'[^\w\s]', '', slug) # remove all punctuation
    slug = re.sub(r'\s+', '-', slug).strip('-') # replace spaces with dashes
    slug = slug.lower()
    return slug


def html_converter(article):
    prompt = (f"Please convert this entire news article to html, where each line is a p tag. Also, format the article with a maximum of three h4 subheadings where possible: {article}")
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=2042,
        temperature=0,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    html_article = response["choices"][0]["text"]
    # print(html_article)
    return html_article


def generate_html_list(html_article):
    prompt = (f"Please generate a html formatted, unordered list of short bullet points about the key information in the following article. Try to only include a maximum of 5 bullet points: {html_article}")
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=2042,
        temperature=0,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    html_list = response["choices"][0]["text"]
    # print(html_list)
    return html_list


def get_categories(topic):
    topic = topic.lower()
    if topic == 'world':
        categories = [5]
    elif topic == 'science':
        categories = [33]
    elif topic == 'uk':
        categories = [42]
    elif topic == 'us':
        categories = [6]
    else:
        raise Exception('Please provide one of the following arguments: world, science, tech, business, uk, us')

    return categories


def generate_image(headline):
    stability_api = client.StabilityInference(
        key=environ.get('STABILITY_KEY'),
        verbose=True,
    )

    sd_prompt = f"an oil painting (with no frame) that best visualises the following news headline: {headline}"

    answers = stability_api.generate(
        prompt=sd_prompt
    )

    for resp in answers:
        for artifact in resp.artifacts:
            if artifact.finish_reason == generation.FILTER:
                raise Exception('Safety filters activated, please remove inappropriate prompt.')
            if artifact.type == generation.ARTIFACT_IMAGE:
                img = Image.open(io.BytesIO(artifact.binary))
                img.save(path.join(basedir, 'images', 'image.png'), 'PNG')


def upload_image():
    endpoint = "https://newsnotfound.com/wp-json/wp/v2/"

    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images', 'image.png'), "rb") as f:
        file = {
            "file": f,
            "content_type": "image/png"
        }
        image_response = requests.post(
            endpoint + "media",
            headers=wordpress_header,
            files=file
        )

    image_id = image_response.json().get("id")
    return image_id


def create_wordpress_post(article, headline, excerpt, slug, categories, image_id):
    api_url = 'https://newsnotfound.com/wp-json/wp/v2/posts'
    data = {
    'title' : headline,
    'excerpt': excerpt,
    'status': 'publish',
    'slug' : slug,
    'content': article,
    "categories": categories,
    "featured_media": image_id
    }
    response = requests.post(api_url,headers=wordpress_header, json=data)
    return response


def escape_quotes(list_of_strings):
    escaped_list = []
    for item in list_of_strings:
        escaped_item = item.replace("'", "\\'").replace('"', '\\"').replace('‘', '\\‘').replace('’', '\\’').replace(',', '\\,')
        escaped_list.append(escaped_item)
    return escaped_list


def unescape_quotes(list_of_strings):
    unescaped_list = []
    for item in list_of_strings:
        unescaped_item = item.replace("\\'", "'").replace('\\"', '"').replace('\\‘', '‘').replace('\\’', '’').replace('\\,', ',')
        unescaped_list.append(unescaped_item)
    return unescaped_list


def format_article(article):
    sentences = re.split(r'(?<=[a-z])[.!?](?=\s+[A-Z])', article)

    # print(sentences)

    formatted_sentences = []
    for sentence in sentences:
        sentence = sentence.strip()
        if sentence[-1] == ".":
            sentence = sentence[:-1]
        sentence = sentence + "."
        sentence = "\n\n" + sentence[0].upper() + sentence[1:]
        formatted_sentences.append(sentence)

    formatted_article = ''.join(formatted_sentences)
    return formatted_article

    
def create_covered_csv():
    file_path = 'covered.csv'
    if not os.path.exists(file_path):
        with open('covered.csv', 'w', newline='') as file:
            fieldnames = ['headline', 'time']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            file.close()


def check_covered(headlines):
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'covered.csv'), 'r') as file:
        reader = csv.DictReader(file)
        for headline in headlines:
            for row in reader:
                if row['headline'] == headline:
                    file.close()
                    return True
        file.close()
        return False

    
def mark_covered(headlines):
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'covered.csv'), 'a') as file:
        writer = csv.writer(file)
        for headline in headlines:
            now = datetime.datetime.now().strftime('%H:%M:%S')
            writer.writerow([headline, now])
        file.close()


def check_relevance(headlines):
    # print(headlines)
    recursive_count = len(headlines)
    while len(headlines) > 2:
        if recursive_count == 0:
            break

        # print(len(headlines))
        stop_words = set(stopwords.words("english"))

        word_freq = {}
        for headline in headlines:
            words = word_tokenize(headline)
            for word in words:
                if word not in stop_words:
                    if word in word_freq:
                        word_freq[word] += 1
                    else:
                        word_freq[word] = 1

        headline_freq = []
        for headline in headlines:
            words = word_tokenize(headline)
            frequency = 0
            for word in words:
                if word not in stop_words:
                    frequency += word_freq[word]
            headline_freq.append(frequency)

        average_freq = sum(headline_freq) / len(headline_freq)

        odd_headline = None
        for i in range(len(headlines)):
            if headline_freq[i] < average_freq * 0.8:
                odd_headline = headlines[i]
                break

        if odd_headline:
            headlines.remove(odd_headline)
        else:
            print("No odd headlines found.")
        
        recursive_count -= 1

    return headlines

# Scale: 5 = neutral, 10 = very positive, 0 = very negative
def calculate_bias(text):
    quoted_text = re.findall(r'[‘’“”\'\"].*?[‘’“”\'\"]', text)

    # Replace the quoted text with an empty string
    for quote in quoted_text:
        text = text.replace(quote, '')
    
    blob = TextBlob(text)
    total_sentiment = 0
    num_sentences = 0
    for sentence in blob.sentences:
        if sentence.sentiment.polarity != 0:
            total_sentiment += sentence.sentiment.polarity
            num_sentences += 1
    if num_sentences == 0:
        bias_rating = 5
    else:
        avg_sentiment = total_sentiment / num_sentences
        bias_rating = int(5 + 5 * avg_sentiment)
    return bias_rating


if __name__ == '__main__':
    main()