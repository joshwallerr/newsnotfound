# Cron set to run this script every 6 hours

from scrape import headlines_links, scrape_articles, get_urls
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
from social import reddit_post, ig_post_image, generate_ig_caption, generate_ig_hashtags, generate_fb_caption, fb_post_image
from choose_headlines import find_most_suitable_headlines


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
    CATEGORY = sys.argv[1]

    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'headlines_links.json')) as f:
        all_headlines_links = json.load(f)[CATEGORY]

    # Choose the most suitable list of headlines
    chosen_headlines = find_most_suitable_headlines(CATEGORY)
    print(chosen_headlines)

    # Scrape articles
    scraped_articles = scrape_articles(chosen_headlines, all_headlines_links)
    print(scraped_articles)

    try:
        # Get facts from scraped articles
        facts = get_facts(scraped_articles)
    except:
        # Choose longest article if max tokens exceeded
        scraped_article = choose_longest(scraped_articles)
        facts = get_facts(scraped_article)
    print('------------ FACTS ------------\n')
    print(facts)


    # Create article brief
    brief = generate_brief(facts)
    print('------------ BRIEF ------------\n')
    print(brief)

    # Generate article
    article = generate_article(brief)
    # print(article)

    print('--------------- ARTICLE SEPARATOR ------------------')

    # Check for, and remove bias
    article = bias_checker(article)
    print(article)

    # AI Bias reviewer and editor?

    # Formatting to start a new line after every sentence
    article = format_article(article)
    print('--------------- ARTICLE SEPARATOR ------------------')
    print(article)

    # Generate headline
    article_headline = generate_headline(article)
    # print(article_headline)

    # Prevent default output - temporary bug fix
    if 'WHO Study Links Air Pollution to Increased' in article_headline or 'WHO' in article_headline and 'Air Pollution' in article_headline:
        raise Exception('Default article generated. Failed run.')

    # Generate excerpt
    article_excerpt = generate_excerpt(article)
    # print(article_excerpt)

    # Generate slug
    article_slug = generate_slug(article_headline)
    # print(article_slug)

    # Convert article to html
    html_article = html_converter(article)
    # print(html_article)

    # Generate html list
    html_list = generate_html_list(html_article)
    print('--------------- HTML LIST SEPARATOR ------------------')
    print(html_list)

    # GENERATE SOURCES LIST
    links_to_headlines = get_urls(chosen_headlines, all_headlines_links)

    sources = dict(zip(chosen_headlines, links_to_headlines))
    print(sources)

    sources_html = generate_sources_list(sources)
    print(sources_html)

    # Combine and prepare article content
    html_content = f'<h3 class=\"title_seps\">At a glance</h3>{html_list}<h3 class=\"title_seps\">The details</h3>{html_article}<h3 id=\"sources-head\">Sources</h3><div id=\"sources-list\">{sources_html}</div>'

    # Get categories
    category_ids = get_categories(CATEGORY)

    # Generate post image and get id
    generate_image(article_headline)
    image_id_url = upload_image()
    featured_media_id = image_id_url[0]
    featured_media_url = image_id_url[1]

    # Create Wordpress post
    response_code = create_wordpress_post(html_content, article_headline, article_excerpt, article_slug, category_ids, featured_media_id)
    print(response_code)

    # if 200 <= response_code.status_code <= 299:
    if response_code.ok:
        # Mark chosen headlines as covered
        mark_covered(chosen_headlines)
        print('Successfully pushed post to Wordpress!')
    else:
        raise Exception('Could not push to Wordpress')

    social_exclusions = ['tyneside']
    reddit_exclusions = ['teesside', 'tyneside']

    if CATEGORY in social_exclusions:
        return

    if CATEGORY not in reddit_exclusions:
        # Post on subreddit
        reddit_post(article_headline, article_slug)

    # Get Instagram hashtags
    ig_tags = generate_ig_hashtags(CATEGORY)

    # Get IG caption
    if article_excerpt == None:
        fb_caption = generate_fb_caption(article_headline, article_slug)
        ig_caption = generate_ig_caption(article_headline, ig_tags)
    else:
        fb_caption = generate_fb_caption(article_excerpt, article_slug)
        ig_caption = generate_ig_caption(article_excerpt, ig_tags)

    # Post Facebook image
    fb_post_image(fb_caption, featured_media_url)

    # Post Instagram image
    ig_post_image(ig_caption, featured_media_url)


def choose_longest(articles):
    longest = 0
    longest_article = ['']
    for article in articles:
        if len(article) > longest:
            longest = len(article)
            longest_article[0] = article

    return longest_article


def get_facts(articles):
    points = []
    for article in articles:
        if len(article) <= 10:
            # print('Passing article')
            continue
        
        print('------------ ARTICLE ------------\n')
        print(article)

        prompt = f'Based on the following article, please create as many bullet points as you can about all of the information. Please keep the bullet points as neutral and unbiased as possible, and feel free to change the wording of things (except quotes) to remove any biased tones and language - stick to neutral facts only. Please only output the bulleted list, nothing else. \n\n{article}'
        
        while(True):
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": prompt},
                ],
                temperature=0,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )

            points.append(response['choices'][0]['message']['content'])
            print(response['choices'][0]['message']['content'])
            break
    return points


def generate_brief(bullet_points):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": 'I have this python list of bullet points, where each list item is a different collection of bullet pointed facts about a news story that have been generated by GPT3 from multiple different scraped news articles on the story. Your job is to filter and combine these facts, and generate a very detailed and informative brief for a news reporter based on all of the available facts and information about the news story. Leave out no information. Your only output should be the brief so it can be stored as a string in python.\n\n' + str(bullet_points)},
        ],
        temperature=0.7,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    return response['choices'][0]['message']['content']


def generate_article(brief):
    prompt = (f"Based on the below brief, please generate me a whole news article for use on a news company's website. The article must be completely unbiased and wrote from a neutral point of view. Please make the article as long and detailed as possible, with as much information as you can fit. Do not write any conclusion. Do not make any assumptions or add any suggestive language. Strictly stick to the facts given to you in the brief. Please write in the inverted pyramid format, and lay the content out so that each sentence is its own paragraph. Please also try to ensure no more than 25% of sentences contain more than 20 words:\n\n{brief}")

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": prompt},
        ],
        temperature=0,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    article = response['choices'][0]['message']['content']
    return article


def bias_checker(article):
    para_list = article.split("\n")
    para_list = [item.strip() for item in para_list if item.strip() != ""]

    new_paras = []
    for para in para_list:
        prompt = (f"You must take on the role of an article reviewer and editor for an unbiased news company. Your job is to look at the below paragraph and ensure that it is 100% neutral and unbiased. If you find any instances of biased words/phrases, or positive/negative language, you must rewrite or reword them in a completely unbiased and neutral way. Aim to be factual, not opinionated.\n\n{para}")
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt},
            ],
            temperature=0,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        new_paras.append(response['choices'][0]['message']['content'])
    article = " ".join(new_paras)
    bias_rating = calculate_bias(article)
    print(bias_rating)

    return article

def generate_headline(article):
    prompt = (f"You must take on the role of an article reviewer and editor for an unbiased news company. Your job is to look at the below article and generate a 100% neutral and unbiased headline. The headline should use completely neutral and unbiased language. Aim to be factual, not opinionated. Keep the headline as short as possible (ideally no more than 10 words). The headline does not need to be overly descriptive, it just needs to inform the reader quickly on what the subject of the article is. Just output the headline.\n\n{article}")
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt},
        ],
        temperature=0.1,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    article_headline = response['choices'][0]['message']['content']

    if len(article_headline) > 120:
        prompt = (f"You must take on the role of an article reviewer and editor for an unbiased news company. Your job is to look at the below article and generate a 100% neutral and unbiased headline. The headline should use completely neutral and unbiased language. Aim to be factual, not opinionated. Keep the headline as short as possible (ideally no more than 10 words). The headline does not need to be overly descriptive, it just needs to inform the reader quickly on what the subject of the article is. Just output the headline.\n\n{article}")
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt},
            ],
            temperature=0.5,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        article_headline = response['choices'][0]['message']['content']

    if article_headline == '':
        raise Exception('Failed to generate headline.')

    if 'Headline: ' in article_headline:
        article_headline = article_headline.replace("Headline: ", "")

    # print(article_headline)
    return article_headline


def generate_excerpt(article):
    prompt = (f"Please generate me a short, unbiased excerpt for the below news article. The excerpt should be relatively short, and no more than one sentence long. Please just output the excerpt: {article}")
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt},
        ],
        temperature=0.1,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    article_excerpt = response['choices'][0]['message']['content']

    if article_excerpt == '':
        return None
    return article_excerpt


def generate_slug(headline):
    slug = headline
    slug = re.sub(r'[^\w\s]', '', slug) # remove all punctuation
    slug = re.sub(r'\s+', '-', slug).strip('-') # replace spaces with dashes
    slug = slug.lower()
    return slug


def html_converter(article):
    prompt = (f"Please convert this entire news article to html, where each line is a p tag. Also, format the article with a maximum of three h4 subheadings where possible: {article}")
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt},
        ],
        temperature=0,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    html_article = response['choices'][0]['message']['content']
    # print(html_article)
    return html_article


def generate_html_list(html_article):
    prompt = (f"Please generate a html formatted, unordered list (<ul>) of short bullet points about the key information in the following article. Try to only include a maximum of 5 bullet points: {html_article}")
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt},
        ],
        temperature=0,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    html_list = response['choices'][0]['message']['content']
    # print(html_list)
    return html_list


def generate_sources_list(sources):
    prompt = (f"Please generate a html formatted, unordered list of sources for the following python dictionary of sources. Each source should be its own list item, and should link to the sources url in a new tab (using target='_blank'). Sources {sources}")
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt},
        ],
        temperature=0,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    sources_list = response['choices'][0]['message']['content']
    print(sources_list)
    return sources_list


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
    elif topic =='teesside':
        categories = [83]
    elif topic == 'tyneside':
        categories = [85]
    else:
        raise Exception('Please provide one of the following arguments: world, science, tech, business, uk, us')

    return categories


def generate_image(headline):
    stability_api = client.StabilityInference(
        key=environ.get('STABILITY_KEY'),
        verbose=True,
    )

    sd_prompt = f"an image in the style of an oil painting that best visualises the following news headline: {headline}"

    answers = stability_api.generate(
        prompt=sd_prompt
    )

    for resp in answers:
        for artifact in resp.artifacts:
            if artifact.finish_reason == generation.FILTER:
                raise Exception('Safety filters activated, please remove inappropriate prompt.')
            if artifact.type == generation.ARTIFACT_IMAGE:
                img = Image.open(io.BytesIO(artifact.binary))
                img.save(path.join(basedir, 'images', 'image.webp'), 'webp')
                # img.save(path.join(basedir, 'images', 'image.png'), 'png')


def upload_image():
    endpoint = "https://newsnotfound.com/wp-json/wp/v2/"

    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images', 'image.webp'), "rb") as f:
        file = {
            "file": f,
            "content_type": "image/webp"
        }
        image_response = requests.post(
            endpoint + "media",
            headers=wordpress_header,
            files=file
        )

    image_id_url = []
    image_id_url.append(image_response.json().get("id"))
    image_id_url.append(image_response.json().get("source_url"))
    return image_id_url


def create_wordpress_post(article, headline, excerpt, slug, categories, image_id):
    api_url = 'https://newsnotfound.com/wp-json/wp/v2/posts'
    data = {
    'title' : headline,
    'excerpt' : excerpt,
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
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'covered.csv'), 'w', newline='') as file:
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
            writer.writerow([headline])
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