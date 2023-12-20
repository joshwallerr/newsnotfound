from scrape import headlines_links, scrape_articles, get_urls
import openai
from os import environ, path
from dotenv import load_dotenv
import ast
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.tokenize import sent_tokenize
import csv
import datetime
import os
import re
from textblob import TextBlob
import base64
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import io
from PIL import Image
from stability_sdk import client
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
import json
import sys
from social import reddit_post, ig_post_image, generate_ig_caption, generate_ig_hashtags, generate_fb_caption, fb_post_image
from choose_headlines import find_most_suitable_headlines
import litellm
from litellm import completion


basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'api_picker.txt'), 'r+') as f:
    content = f.read().strip()
    if content == '1':
        api_key = environ.get('OPENAI_API_KEY')
        print('using key 1')
    elif content == '2':
        api_key = environ.get('OPENAI_API_KEY_2')
        print('using key 2')
    else:
        raise Exception('No API key available')

    # Seek to the beginning of the file before writing
    f.seek(0)

    # Write to the file
    f.write('2' if content == '1' else '1')

    # Truncate the file to the current position to remove any leftover characters
    f.truncate()

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
    # TEMPORARILY DISABLED
    # article = bias_checker(article)
    # print(article)

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

    # Generate post image and get id
    img_prompt = generate_image(article_headline)
    image_id_url = upload_image()
    featured_media_id = image_id_url[0]
    featured_media_url = image_id_url[1]

    # GENERATE SOURCES LIST
    links_to_headlines = get_urls(chosen_headlines, all_headlines_links)

    sources = dict(zip(chosen_headlines, links_to_headlines))
    print(sources)

    sources_html = generate_sources_list(sources)
    print(sources_html)

    # GENERATE X-RAY SECTION
    source_names = get_source_names(links_to_headlines)
    print(source_names)

    separate_facts = facts_to_lists(facts)

    xray_html = generate_xray(sources_html, img_prompt, source_names, separate_facts)

    ossummary = generate_ossummary(article)

    # Combine and prepare article content
    html_content = f'<p class=\"title_seps\"><strong>One sentence summary</strong> - {ossummary}</p><h3 class=\"title_seps\">At a glance</h3>{html_list}<h3 class=\"title_seps\">The details</h3>{html_article}<h3 id=\"sources-head\">Article X-ray</h3>{xray_html}'

    # Get categories
    category_ids = get_categories(CATEGORY)

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

    social_exclusions = ['cybersecurity', 'ai', 'uk_education', 'uk_construction', 'us_politics', 'crypto', 'us_agriculture', 'tyneside', 'sunderland', 'worcester', 'bedford', 'norwich', 'west_yorkshire', 'plymouth', 'india', 'brazil', 'turkey', 'uk', 'world', 'science', 'us', 'uk_politics', 'technology', 'finance_energy_solar', 'finance_energy_wind', 'finance_energy_gas', 'finance_energy_hydro', 'china', 'finance_commodities', 'uk_agriculture']

    if CATEGORY in social_exclusions:
        return

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
    """
    This function takes a list of articles and returns the article with the longest length.
    """
    longest = 0
    longest_article = ['']
    for article in articles:
        if len(article) > longest:
            longest = len(article)
            longest_article[0] = article

    # check the index of the chosen article and return it to the main function. Then update chosen headlines to inculde only the 3rd headline for example, if the third article was the longest.

    return longest_article


def get_facts(articles):
    """
    This function takes a list of articles, prompts GPT-3 to create bullet points about the
    information in each article, and returns a list of bullet points for each article.
    """
    points = []
    for article in articles:
        if len(article) <= 10:
            # print('Passing article')
            continue
        
        print('------------ ARTICLE ------------\n')
        print(article)

        prompt = f'Based on the following article, please create as many bullet points as you can about all of the information. Please keep the bullet points as neutral and unbiased as possible, and feel free to change the wording of things (except quotes) to remove any biased tones and language - stick to neutral facts only. Please only output the bulleted list, nothing else. \n\n{article}'
        
        while(True):
            response = completion(
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
    """
    This function generates a detailed and informative news brief by filtering and combining bullet
    points generated by GPT3 from multiple news articles.
    """
    response = completion(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": "What makes a good, well written, and informative news article brief about a news story? In this case, it is important that the brief is unbiased and written from a completely neutral perspective."},
            {"role": "assistant", "content": "A good, well-written, and informative news article brief should have the following characteristics:\n\n1. Clarity and conciseness: The brief should be written in a clear and concise manner, using simple language that is easy to understand. It should avoid jargon and complex sentences.\n\n2. Accuracy: The brief should be factually accurate, with all information sourced from reliable and credible sources. Any data or statistics used should be up-to-date and verifiable.\n\n3. Objectivity: The brief should be written from a neutral perspective, without any bias or personal opinions. It should present the facts and allow readers to form their own opinions.\n\n4. Balance: The brief should present all relevant sides of the story, giving equal weight to different perspectives and viewpoints. It should not favor one side over another.\n\n5. Relevance: The brief should focus on the most important and relevant aspects of the news story, highlighting the key points that readers need to know.\n\n6. Timeliness: The brief should be up-to-date and timely, reflecting the latest developments in the news story.\n\n7. Structure: The brief should be well-organized, with a logical flow of information. It should start with a strong lead that summarizes the main points of the story, followed by supporting details and background information.\n\n8. Attribution: The brief should clearly attribute all information, quotes, and sources used, giving credit where it is due.\n\n9. Proper grammar and spelling: The brief should be free of grammatical errors and spelling mistakes, ensuring that it is professional and easy to read.\n\n10. Engaging tone: While maintaining objectivity, the brief should be written in an engaging and interesting tone that captures the reader's attention and encourages them to read further."},
            {"role": "user", "content": 'I have this python list of bullet points, where each list item is a different collection of bullet pointed facts about a news story that have been generated by GPT3 from multiple different scraped news articles on the story. Your job is to filter and combine these facts, and generate a very detailed and informative brief for a news reporter based on all of the available facts and information about the news story. Leave out no information. Your only output should be the brief so it can be stored as a string in python.\n\n' + str(bullet_points)},
        ],
        temperature=0.7,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    return response['choices'][0]['message']['content']


def generate_article(brief):
    """
    This function generates an unbiased news article based on a given brief using GPT-4.
    """
    prompt = (f"Based on the below brief, please generate me a whole news article for use on a news company's website. The article must be completely unbiased and wrote from a neutral point of view. Please make the article as long and detailed as possible, with as much information as you can fit. Do not write any conclusion. Do not make any assumptions or add any suggestive language. Strictly stick to the facts given to you in the brief. Please write in the inverted pyramid format, and lay the content out so that each sentence is its own paragraph. Please also try to ensure no more than 25% of sentences contain more than 20 words:\n\n{brief}")

    api_key = environ.get('OPENAI_API_KEY')
    openai.api_key = api_key
    print('switching to api key 1')

    response = completion(
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

    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'api_picker.txt'), 'r+') as f:
        content = f.read().strip()
        if content == '1':
            api_key = environ.get('OPENAI_API_KEY_2')
            openai.api_key = api_key
            print('switching back to api key 2')

    return article


def bias_checker(article):
    """
    This function takes an article as input, checks for biased language and rewrites it in a neutral way
    using GPT-3, and then calculates the bias rating of the resulting article.
    """
    para_list = article.split("\n")
    para_list = [item.strip() for item in para_list if item.strip() != ""]

    new_paras = []
    for para in para_list:
        prompt = (f"You must take on the role of an article reviewer and editor for an unbiased news company. Your job is to look at the below paragraph and ensure that it is 100% neutral and unbiased. If you find any instances of biased words/phrases, or positive/negative language, you must rewrite or reword them in a completely unbiased and neutral way. Aim to be factual, not opinionated. If a paragraph is already neutral and unbiased, just output the original paragraph.\n\n{para}")
        response = completion(
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
    """
    This function generates a neutral and unbiased headline for a given article using GPT-3.
    """
    prompt = (f"You must take on the role of an article reviewer and editor for an unbiased news company. Your job is to look at the below article and generate a 100% neutral and unbiased headline. The headline should use completely neutral and unbiased language. Aim to be factual, not opinionated. Keep the headline as short as possible (ideally no more than 10 words). The headline does not need to be overly descriptive, it just needs to inform the reader quickly on what the subject of the article is. Just output the headline.\n\n{article}")
    response = completion(
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
        response = completion(
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

    # Prefix removal
    if 'Neutral and unbiased: ' in article_headline:
        article_headline = article_headline.replace("Neutral and unbiased: ", "")

    if 'Neutral and unbiased headline: ' in article_headline:
        article_headline = article_headline.replace("Neutral and unbiased headline: ", "")

    if 'Neutral and unbiased version: ' in article_headline:
        article_headline = article_headline.replace("Neutral and unbiased version: ", "")

    if 'Headline: ' in article_headline:
        article_headline = article_headline.replace("Headline: ", "")

    # Remove period
    if article_headline[-1] == '.':
        article_headline = article_headline[:-1]

    # print(article_headline)
    return article_headline


def generate_excerpt(article):
    """
    This function uses GPT-3 to generate a short, unbiased excerpt for a given news article.
    """
    prompt = (f"Please generate me a short, unbiased excerpt for the below news article. The excerpt should be relatively short, and no more than one sentence long. The excerpt must be completely impartial and written from a neutral point of view. Please just output the excerpt: {article}")
    response = completion(
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


    # Length check - make sure excerpt is no more than one sentence long
    
    num_sentences = len(sent_tokenize(article_excerpt))
    if num_sentences > 1 or article_excerpt == '':
        prompt = (f"Please generate me a short, unbiased excerpt for the below news article. The excerpt should be relatively short, and no more than one sentence long. The excerpt must be completely impartial and written from a neutral point of view. Please just output the excerpt: {article}")
        response = completion(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt},
            ],
            temperature=0.5,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        article_excerpt = response['choices'][0]['message']['content']

    return article_excerpt


def generate_slug(headline):
    """
    This function generates a URL-friendly slug from a given headline by removing punctuation, replacing
    spaces with dashes, and converting to lowercase.
    """
    slug = headline
    slug = re.sub(r'[^\w\s]', '', slug) # remove all punctuation
    slug = re.sub(r'\s+', '-', slug).strip('-') # replace spaces with dashes
    slug = slug.lower()
    return slug


def html_converter(article):
    """
    This function uses GPT-3 to convert a news article (string) into HTML format with a
    maximum of three h4 subheadings.
    """
    prompt = (f"Please convert this entire news article to html, where each line is a p tag. Also, format the article with a maximum of three h4 subheadings where possible: {article}")
    response = completion(
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
    """
    This function uses GPT-3 to generate an HTML-formatted unordered list of short bullet 
    points summarizing key information in an article.
    """
    prompt = (f"Please generate a html formatted, unordered list (<ul>) of short bullet points about the key information in the following article. Try to only include a maximum of 5 bullet points: {html_article}")
    response = completion(
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
    """
    This function returns an HTML-formatted, unordered list of sources from a Python dictionary and
    returns the list.
    """
    prompt = (f"Please generate a html formatted, unordered list of sources for the following python dictionary of sources. Each source should be its own list item, and should link to the sources url in a new tab (using target='_blank'). Sources {sources}")
    response = completion(
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


def get_source_names(source_urls):
    """
    This function takes in a list of source URLs and returns the source names as a list of domains.
    """
    from urllib.parse import urlparse

    source_names = []
    for url in source_urls:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc

        # Remove 'www.' if present
        if domain.startswith('www.'):
            domain = domain[4:]

        source_names.append(domain)

    return source_names


def generate_xray(sources_html, image_prompt, source_names, facts):
    fact_table = ''.join([f"""
    <table class="tg">
    <thead>
      <tr>
        <th class="tg-0pky">{source}</th>
      </tr>
    </thead>
    <tbody>
      {"".join([f"<tr><td class='tg-c3ow'>{fact}</td></tr>" for fact in source_facts])}
    </tbody>
    </table>
    """ for source, source_facts in zip(source_names, facts)])

    xray_html = f"""
    <div class="taccordion-div">
        <button class="taccordion">Sources</button>
        <div class="tpanel">
            <div id=\"sources-list\">
                <p>Here are all the sources used to create this article:</p>{sources_html}
            </div>
        </div>
    </div>
    <div class="taccordion-div">
        <button class="taccordion">Image prompt</button>
        <div class="tpanel">
            <p>{image_prompt}</p>
        </div>
    </div>
    <div class="taccordion-div">
        <button class="taccordion">Fact attribution</button>
        <div class="tpanel">
            <p>This section links each of the article's facts back to its original source.</p>
            <p>If you have any suspicions that false information is present in the article, you can use this section to investigate where it came from.</p>
            {fact_table}
        </div>
    </div>
    """
    return xray_html


def get_categories(topic):
    """
    This function takes a topic (news category e.g. world, science) as input and returns a list of
    wordpress category id's that correspond with the topic.
    """
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
        categories = [42, 83]
    elif topic == 'tyneside':
        categories = [42, 85]
    elif topic == 'sunderland':
        categories = [42, 86]
    elif topic == 'worcester':
        categories = [42, 87]
    elif topic == 'bedford':
        categories = [42, 88]
    elif topic == 'norwich':
        categories = [42, 89]
    elif topic == 'west_yorkshire':
        categories = [42, 90]
    elif topic == 'plymouth':
        categories = [42, 91]
    elif topic == 'india':
        categories = [92]
    elif topic == 'brazil':
        categories = [98]
    elif topic == 'turkey':
        categories = [99]
    elif topic == 'uk_politics':
        categories = [100]
    elif topic == 'technology':
        categories = [103]
    elif topic == 'finance_energy_solar':
        categories = [107]
    elif topic == 'finance_energy_wind':
        categories = [108]
    elif topic == 'finance_energy_gas':
        categories = [109]
    elif topic == 'finance_energy_hydro':
        categories = [110]
    elif topic == 'china':
        categories = [111]
    elif topic == 'finance_commodities':
        categories = [112]
    elif topic == 'uk_agriculture':
        categories = [112, 116]
    elif topic == 'us_agriculture':
        categories = [112, 117]
    elif topic == 'crypto':
        categories = [118]
    elif topic == 'us_politics':
        categories = [119]
    elif topic == 'uk_construction':
        categories = [122]
    elif topic == 'uk_education':
        categories = [125]
    elif topic == 'ai':
        categories = [127]
    elif topic == 'cybersecurity':
        categories = [128]
    else:
        raise Exception('Please provide one of the following arguments: world, science, tech, business, uk, us')

    return categories


def generate_ossummary(article):
    """
    This function takes an article as input and returns a one sentence summary of the article.
    """
    prompt = (f"Please generate a one sentence summary of the following article. The summary must be completely unbiased and written neutrally: {article}")
    response = completion(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt},
        ],
        temperature=0,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    summary = response['choices'][0]['message']['content']
    # print(summary)
    return summary


def generate_image(headline):
    """
    This function generates an image in the style of an oil painting based on a given news headline using
    the Stability API.

    It will return the prompt used for use in the x-ray section.
    """
    stability_api_key = environ.get('STABILITY_KEY')
    engine_id = "stable-diffusion-xl-beta-v2-2-2"

    api_host = os.getenv('API_HOST', 'https://api.stability.ai')
    url = f"{api_host}/v1/engines/list"

    if stability_api_key is None:
        raise Exception("Missing Stability API key.")

    try:
        # Generate unique prompt
        prompt = (f'write me a short, one sentence long text-to-image prompt that best visualises the following headline: {headline}\n\nThe image will be in the style of pixel art, but there is no need to specify this.\n\nKeep it extremely simple and dont be too specific.\n\nThe image engine does not handle words well, so under no circumstances should you ask it to write words onto the image.\n\nFor best results, do not go into detail.')
        response = completion(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        sd_prompt = response['choices'][0]['message']['content']
    except:
        sd_prompt = (f"an image that best visualises the following news headline: {headline}")

    response = requests.post(
        f"{api_host}/v1/generation/{engine_id}/text-to-image",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {stability_api_key}"
        },
        json={
            "text_prompts": [
                {
                    "text": sd_prompt,
                }
            ],
            "cfg_scale": 7,
            "clip_guidance_preset": "NONE",
            "height": 512,
            "width": 512,
            "samples": 1,
            "steps": 50,
            "style_preset": "pixel-art",
        },
    )

    if response.status_code != 200:
        raise Exception("Non-200 response: " + str(response.text))

    data = response.json()

    print(data['artifacts'][0]['finishReason'])

    if data['artifacts'][0]['finishReason'] == "CONTENT_FILTERED":
        return generate_image(headline)

    for i, image in enumerate(data["artifacts"]):
        with open(path.join(basedir, 'images', 'image.webp'), "wb") as f:
            f.write(base64.b64decode(image["base64"]))

    return sd_prompt


def upload_image():
    """
    This function uploads the image file to WordPress and returns the image ID and source URL.
    """
    endpoint = "https://newsnotfound.com/wp-json/wp/v2/"
    session = requests.Session()
    retry = Retry(total=5, backoff_factor=0.1, status_forcelist=[ 500, 502, 503, 504 ])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images', 'image.webp'), "rb") as f:
        file = {
            "file": f,
            "content_type": "image/webp"
        }
        image_response = session.post(
            endpoint + "media",
            headers=wordpress_header,
            files=file
        )

    image_id_url = []
    image_id_url.append(image_response.json().get("id"))
    image_id_url.append(image_response.json().get("source_url"))
    return image_id_url


def create_wordpress_post(article, headline, excerpt, slug, categories, image_id):
    """
    This function creates a WordPress post with specified parameters such as article content, headline,
    excerpt, slug, categories, and image ID.
    """
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
    """
    This function takes a list of strings and returns a new list with all single and
    double quotes, as well as certain punctuation marks, escaped with a backslash.
    """
    escaped_list = []
    for item in list_of_strings:
        escaped_item = item.replace("'", "\\'").replace('"', '\\"').replace('‘', '\\‘').replace('’', '\\’').replace(',', '\\,')
        escaped_list.append(escaped_item)
    return escaped_list


def unescape_quotes(list_of_strings):
    """
    This function takes a list of strings and replaces escaped quotes and commas with
    their unescaped counterparts.
    """
    unescaped_list = []
    for item in list_of_strings:
        unescaped_item = item.replace("\\'", "'").replace('\\"', '"').replace('\\‘', '‘').replace('\\’', '’').replace('\\,', ',')
        unescaped_list.append(unescaped_item)
    return unescaped_list


def facts_to_lists(facts):
    """
    This function takes a list of facts and returns a new list for every list in facts, where each new list
    is another list containing one sentence from the original list of facts.
    """
    import spacy

    new_facts_list = []

    nlp = spacy.load("en_core_web_sm")

    for fact_set in facts:
        doc = nlp(fact_set)
        sentences = [sent.text for sent in doc.sents]
        new_facts_list.append(sentences)

    return new_facts_list


def format_article(article):
    """
    This function takes an article as input, splits it into sentences, formats each sentence with proper
    capitalization and spacing, and returns the formatted article.
    """
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
    """
    This function creates a CSV file with specified field names if it does not already exist.
    """
    file_path = 'covered.csv'
    if not os.path.exists(file_path):
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'covered.csv'), 'w', newline='') as file:
            fieldnames = ['headline', 'time']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            file.close()


def check_covered(headlines):
    """
    This function checks if any of the headlines in a given list are present in a CSV file called
    'covered.csv'.
    """
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
    """
    The function writes a list of headlines to a CSV file named "covered.csv".
    """
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'covered.csv'), 'a') as file:
        writer = csv.writer(file)
        for headline in headlines:
            writer.writerow([headline])
        file.close()


def check_relevance(headlines):
    """
    This function takes a list of headlines, removes the one that is least relevant based on word
    frequency, and repeats the process until only two headlines remain.

    NO LONGER IN USE
    """
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
    """
    This function calculates the bias rating of a given text based on the sentiment polarity of its
    sentences.
    """
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