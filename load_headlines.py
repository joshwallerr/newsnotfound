from scrape import headlines_links, scrape_articles
import csv
import os
from itertools import zip_longest
from sentence_transformers import SentenceTransformer, util
import json

# Load scraped headlines into headlines.csv
# Load scraped headlines into headlines.csv
# Load scraped headlines into headlines.csv

world_urls = [
    'https://www.reuters.com/world/'
    'https://www.telegraph.co.uk/world-news/',
    'https://apnews.com/hub/world-news',
    'https://www.washingtonpost.com/world/',
    'https://news.sky.com/world',
    'https://www.bbc.co.uk/news/world'
]

science_urls = [
    'https://www.bbc.co.uk/news/science_and_environment'
    'https://www.theguardian.com/science',
    'https://www.independent.co.uk/news/science',
    'https://www.newscientist.com/section/news/',
    'https://scitechdaily.com/news/science/'
]

uk_urls = [
    'https://www.bbc.co.uk/news/uk'
    'https://www.reuters.com/world/uk/',
    'https://www.theguardian.com/uk-news',
    'https://news.sky.com/uk',
    'https://www.independent.co.uk/news/uk'
]

us_urls = [
    'https://www.theguardian.com/us-news'
    'https://www.reuters.com/world/us/',
    'https://www.bbc.co.uk/news/world/us_and_canada',
    'https://eu.usatoday.com/',
    'https://www.independent.co.uk/news/world/americas'
]

teesside_urls = [
    'https://www.gazettelive.co.uk/news/teesside-news/',
    'https://www.thenorthernecho.co.uk/news/local/teesside/',
]

all_urls = {
    'world': world_urls,
    'science': science_urls,
    'uk': uk_urls,
    'us': us_urls,
    'teesside': teesside_urls
}

all_headlines_links = {}
all_headlines = {}
all_links = {}

for category, url_list in all_urls.items():
    scraped_headlines = headlines_links(url_list)
    all_headlines_links[category] = scraped_headlines
    all_headlines[category] = scraped_headlines.keys()
    all_links[category] = scraped_headlines.values()

# Dump all_headlines_links into data/headlines_links.json
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'headlines_links.json'), 'w') as jsonfile:
    json.dump(all_headlines_links, jsonfile, indent=4)

# Open a new file for writing
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'headlines.csv'), 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)

    # Write the header row with the keys from the dictionary
    writer.writerow(all_headlines.keys())

    # Write each row of headlines
    for row in zip_longest(*all_headlines.values(), fillvalue=''):
        writer.writerow(row)


# Load related headlines into related_headlines.csv
# Load related headlines into related_headlines.csv
# Load related headlines into related_headlines.csv

model = SentenceTransformer('paraphrase-distilroberta-base-v2')

def process_headlines(headlines):
    embeddings = model.encode(headlines, convert_to_tensor=True)
    related_headlines = []
    for i, headline in enumerate(headlines):
        sims = util.pytorch_cos_sim(embeddings[i], embeddings)[0]
        indices = sims.argsort(descending=True).tolist()
        related = [(headlines[j], sims[j].item()) for j in indices if sims[j] > 0.5 and j != i]
        if related:
            # related.insert(0, ('Similarity', 'Score'))
            related_headlines.append(related)
    return related_headlines

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'headlines.csv'), 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    headers = reader.fieldnames
    headlines = {header: [] for header in headers}
    for row in reader:
        for header in headers:
            if row[header].strip():
                headlines[header].append(row[header].strip())

related_headlines = {header: process_headlines(headlines[header]) for header in headers}

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'related_headlines.csv'), 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=headers)
    writer.writeheader()
    max_length = max([len(related_headlines[header]) for header in headers])
    for i in range(max_length):
        row = {}
        for header in headers:
            if i < len(related_headlines[header]):
                row[header] = related_headlines[header][i]
            else:
                row[header] = ''
        writer.writerow(row)
