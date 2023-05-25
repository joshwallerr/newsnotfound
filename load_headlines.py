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
    'https://www.reuters.com/world/',
    'https://www.telegraph.co.uk/world-news/',
    'https://apnews.com/hub/world-news',
    'https://www.washingtonpost.com/world/',
    'https://news.sky.com/world',
    'https://www.bbc.co.uk/news/world',
]

science_urls = [
    'https://www.bbc.co.uk/news/science_and_environment',
    'https://www.theguardian.com/science',
    'https://www.independent.co.uk/news/science',
    'https://www.newscientist.com/section/news/',
    'https://scitechdaily.com/news/science/',
]

uk_urls = [
    'https://www.bbc.co.uk/news/uk',
    'https://www.reuters.com/world/uk/',
    'https://www.theguardian.com/uk-news',
    'https://news.sky.com/uk',
    'https://www.independent.co.uk/news/uk',
]

us_urls = [
    'https://www.theguardian.com/us-news',
    'https://www.reuters.com/world/us/',
    'https://www.bbc.co.uk/news/world/us_and_canada',
    'https://usatoday.com/news/nation/',
    'https://www.independent.co.uk/news/world/americas',
]

teesside_urls = [
    'https://www.gazettelive.co.uk/news/teesside-news/',
    'https://www.thenorthernecho.co.uk/news/local/teesside/',
]

tyneside_urls = [
    'https://www.chroniclelive.co.uk/all-about/newcastle-upon-tyne',
    'https://www.chroniclelive.co.uk/all-about/gateshead',
    # 'https://www.shieldsgazette.com/news/latest',
    # 'https://www.northumberlandgazette.co.uk/news',
    'https://www.thenorthernecho.co.uk/news/local/northdurham/tyneandwear/',
]

sunderland_urls = [
    'https://www.chroniclelive.co.uk/all-about/sunderland',
    'https://www.thenorthernecho.co.uk/local-news/sunderland-news/',
    # 'https://www.sunderlandecho.com/news',
]

worcester_urls = [
    'https://www.worcesternews.co.uk/news/worcester/',
    'https://worcesterobserver.co.uk/news/',
    'https://www.bbc.co.uk/news/england/hereford_and_worcester',
]

bedford_urls = [
    'https://www.bedfordindependent.co.uk/category/news/',
    'https://www.bedfordshirelive.co.uk/news/bedfordshire-news/',
]

norwich_urls = [
    'https://www.eveningnews24.co.uk/news/',
    'https://www.bbc.co.uk/news/england/norfolk',
]

west_yorkshire_urls = [
    'https://www.examinerlive.co.uk/news/west-yorkshire-news/',
    'https://www.bbc.co.uk/news/england/leeds_and_west_yorkshire',
]

plymouth_urls = [
    'https://www.plymouthherald.co.uk/news/plymouth-news/',
    'https://www.bbc.co.uk/news/england/devon',
]

india_urls = [
    'https://www.thehindu.com/news/national/',
    'https://indianexpress.com/section/india/',
    'https://www.bbc.co.uk/news/world/asia/india',
    'https://www.reuters.com/world/india/',
]

brazil_urls = [
    'https://www.aljazeera.com/where/brazil/',
    'https://www.reuters.com/news/archive/brazil',
    'https://www1.folha.uol.com.br/internacional/en/brazil/',
]

turkey_urls = [
    'https://www.aljazeera.com/where/turkey/',
    'https://www.reuters.com/news/archive/turkey',
    'https://www.independent.co.uk/topic/turkey',
]

uk_politics_urls = [
    'https://www.bbc.co.uk/news/politics',
    'https://www.theguardian.com/politics/all',
    'https://www.independent.co.uk/news/uk/politics',
    'https://news.sky.com/politics',
    'https://www.telegraph.co.uk/politics/',
    'https://www.huffingtonpost.co.uk/politics/',
]

technology_urls = [
    'https://www.bbc.co.uk/news/technology',
    'https://news.sky.com/technology',
    'https://www.reuters.com/technology/',
    'https://www.independent.co.uk/tech',
]

finance_energy_solar_urls = [
    'https://www.reuters.com/tags/solar/',
    'https://www.solarpowerportal.co.uk/news/list',
    'https://www.pv-magazine.com/news/',
    'https://www.solarpowerworldonline.com/category/industry-news/',
]

finance_energy_wind_urls = [
    'https://www.reuters.com/tags/wind/',
    'https://www.rechargenews.com/latest',
    'https://www.offshorewind.biz/news/',
    'https://www.windpowermonthly.com/search/articles?NewsTypes=1&HeadlinesOnly=false',
]

finance_energy_gas_urls = [
    'https://www.reuters.com/tags/gas/',
    'https://www.gasworld.com/topics/all-news/',
    'https://www.naturalgasworld.com/news',
]

finance_energy_hydro_urls = [
    'https://www.reuters.com/tags/hydrogen/',
    'https://www.h2-view.com/news/all-news/',
    'https://www.hydrogeninsight.com/latest',
]

china_urls = [
    'https://www.reuters.com/world/china/',
    'https://www.bbc.co.uk/news/world/asia/china',
    'https://www.theguardian.com/world/china',
    'https://www.independent.co.uk/topic/china',
    'https://apnews.com/hub/china',
]

finance_commodities_urls = [
    'https://www.reuters.com/news/archive/GCA-Commodities',
    'https://uk.investing.com/news/commodities-news',
    'https://www.spglobal.com/commodityinsights/en/market-insights/latest-news',
    'https://www.fxstreet.com/news?dFR[Category][0]=News&dFR[Tags][0]=Commodities',
]

# commodities_gold_urls = [
#     'https://www.reuters.com/news/archive/goldMktRpt',
#     'https://www.fxstreet.com/news/latest/asset?dFR[Category][0]=News&dFR[Tags][0]=XAUUSD',
#     'https://www.kitco.com/scripts/news/search.pl?headline=gold&Submit=',
# ]

uk_agriculture_urls = [
    'https://www.farminguk.com/newslist/news',
    'https://www.fwi.co.uk/latest/all-the-latest-farming-news',
    'https://www.agriland.co.uk/latest-farming-news/',
]

us_agriculture_urls = [
    'https://www.agweb.com/news',
    'https://www.agdaily.com/category/news/',
    # 'https://www.farmprogress.com/latest-news', # add scraping for this and done with this category
]

all_urls = {
    'world': world_urls,
    'science': science_urls,
    'uk': uk_urls,
    'us': us_urls,
    'teesside': teesside_urls,
    'tyneside': tyneside_urls,
    'sunderland': sunderland_urls,
    'worcester': worcester_urls,
    'bedford': bedford_urls,
    'norwich': norwich_urls,
    'west_yorkshire': west_yorkshire_urls,
    'plymouth': plymouth_urls,
    'india': india_urls,
    'brazil': brazil_urls,
    'turkey': turkey_urls,
    'uk_politics': uk_politics_urls,
    'technology': technology_urls,
    'finance_energy_solar': finance_energy_solar_urls,
    'finance_energy_wind': finance_energy_wind_urls,
    'finance_energy_gas': finance_energy_gas_urls,
    'finance_energy_hydro': finance_energy_hydro_urls,
    'china': china_urls,
    'finance_commodities': finance_commodities_urls,
    'uk_agriculture': uk_agriculture_urls,
    'us_agriculture': us_agriculture_urls,
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
    """
    This function takes a list of headlines, encodes them using a pre-trained model, and returns a list
    of related headlines based on cosine similarity scores.
    """
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
