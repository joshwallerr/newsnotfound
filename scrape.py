import requests
from bs4 import BeautifulSoup

def headlines_links(urls):
    all_headlines_links = {}

    recursive_count = 0
    for url in urls:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        recursive_count += 16

        if 'telegraph.co.uk' in url:
            for headline in soup.find_all('a', class_='list-headline__link u-clickable-area__link'):
                headline_text = headline.find('span', class_='list-headline__text').find('span').text
                headline_link = 'https://www.telegraph.co.uk' + headline.get('href')
                all_headlines_links[headline_text] = headline_link

        if 'bbc.co.uk' in url:
            for article in soup.find_all('div', class_='gs-c-promo-body'):
                headline = article.find('h3')
                headline_text = headline.text
                headline_link = 'https://www.bbc.co.uk' + article.find('a')['href']
                all_headlines_links[headline_text] = headline_link

        if 'washingtonpost.com' in url:
            for headline in soup.find_all('a', class_='flex hover-blue'):
                headline_text = headline.find('h3', class_='font-md font-bold font--headline lh-sm gray-darkest hover-blue mb-0 antialiased mb-xxs').text
                headline_link = headline.get('href')
                all_headlines_links[headline_text] = headline_link

        if 'theguardian.com' in url:
            for article in soup.find_all('div', class_='fc-item__container'):
                headline = article.find('a', class_='u-faux-block-link__overlay js-headline-text')
                headline_text = headline.text
                headline_link = headline['href']
                all_headlines_links[headline_text] = headline_link

        if 'independent.co.uk' in url:
            if recursive_count > 16:
                recursive_count = 0
                continue

            for article in soup.find_all('a', class_='title'):
                headline_text = article.text
                headline_link = 'https://www.independent.co.uk' + article['href']
                all_headlines_links[headline_text] = headline_link

        if 'newscientist.com' in url:
            for article in soup.find_all('div', class_='card__content'):
                headline_text = article.find('h2', class_='card__heading').text
                headline_link = 'https://www.newscientist.com' + article.find('a')['href']
                all_headlines_links[headline_text] = headline_link

        if 'scitechdaily.com' in url:
            for article in soup.find_all('h3', class_='entry-title'):
                headline = article.find('a')
                headline_text = headline.text
                headline_link = headline['href']
                all_headlines_links[headline_text] = headline_link

        if 'reuters.com' in url:
            for article in soup.find_all('a', attrs={"data-testid": "Heading"}):
                try:
                    headline_text = article.select_one('span').text
                except:
                    headline_text = article.text
                headline_link = 'https://www.reuters.com' + article['href']
                all_headlines_links[headline_text] = headline_link

        if 'apnews.com' in url:
            for article in soup.find_all('a', attrs={"data-key": "card-headline"}):
                headline_text = article.find('h2').text
                headline_link = 'https://apnews.com' + article['href']
                all_headlines_links[headline_text] = headline_link

        if 'news.sky.com' in url:
            for article in soup.find_all('h3', class_='sdc-site-tile__headline'):
                headline = article.find('a', class_='sdc-site-tile__headline-link')
                headline_text = headline.find('span').text
                headline_link = 'https://news.sky.com' + headline['href']
                if '/video/' in headline_link:
                    pass
                else:
                    all_headlines_links[headline_text] = headline_link

        if 'eu.usatoday.com' in url:
            # Get hero item
            main_hero = soup.find('div', class_='section-helper-flex section-helper-row p12-container')
            headline_text = main_hero.find('div', class_='display-4 p12-title').text
            headline_link = main_hero.find('a', class_='p12-container-link')['href']
            all_headlines_links[headline_text] = 'https://eu.usatoday.com' + headline_link

            # Get secondary hero items
            hero_two = soup.find('div', class_='hero-slot-two')
            headline_text = hero_two.find('div', class_='display-6 p13-title').text
            headline_link = hero_two.find('a', class_='section-helper-flex section-helper-row p13-container')['href']
            all_headlines_links[headline_text] = 'https://eu.usatoday.com' + headline_link

            # Get third hero items
            hero_three = soup.find('div', class_='hero-slot-three')
            headline_text = hero_three.find('div', class_='display-6 p13-title').text
            headline_link = hero_three.find('a', class_='section-helper-flex section-helper-row p13-container')['href']
            all_headlines_links[headline_text] = 'https://eu.usatoday.com' + headline_link

            # Get all other headlines
            for article in soup.find_all('a', class_='p1-container'):
                headline = article.find('div', class_='p1-title-spacer')
                headline_text = headline.text
                headline_link = 'https://eu.usatoday.com' + article['href']
                all_headlines_links[headline_text] = headline_link

        if 'newsnotfound.com' in url:
            article_div = soup.find('div', class_='main-banner-block-posts banner-trailing-posts')
            for article in article_div.find_all('h2', class_="post-title"):
                headline_text = article.find('a').text
                headline_link = article.find('a')['href']
                all_headlines_links[headline_text] = headline_link

        if 'gazettelive.co.uk' in url:
            for article in soup.find_all('a', class_="headline"):
                headline_text = article.text
                headline_link = article['href']
                all_headlines_links[headline_text] = headline_link

        if 'thenorthernecho.co.uk' in url:
            # Get hero item
            for article in soup.find_all('a', class_='mar-lead-story__link'):
                headline_text = article.find('span').text
                headline_link = 'https://www.thenorthernecho.co.uk' + article['href']
                if 'lott' in headline_text.lower() or 'forecast' in headline_text.lower() or 'live:' in headline_text.lower() or '-live-' in headline_link:
                    continue
                all_headlines_links[headline_text] = headline_link

            for article in soup.find_all('a', class_='text-slate no-underline'):
                headline_text = article.text
                headline_link = 'https://www.thenorthernecho.co.uk' + article['href']
                if 'lott' in headline_text.lower() or 'forecast' in headline_text.lower() or 'live:' in headline_text.lower() or '-live-' in headline_link:
                    continue
                all_headlines_links[headline_text] = headline_link

        if 'chroniclelive.co.uk' in url:
            for article in soup.find_all('a', class_='headline'):
                headline_text = article.text
                headline_link = article['href']
                if 'lott' in headline_text.lower() or 'forecast' in headline_text.lower() or '-live-' in headline_link or 'live:' in headline_text.lower() or 'recap:' in headline_text.lower():
                    continue
                all_headlines_links[headline_text] = headline_link

        if 'shieldsgazette.com' in url:
            for article in soup.find_all('a', class_='article-title'):
                headline_text = article.text
                headline_link = 'https://www.shieldsgazette.com' + article['href']
                all_headlines_links[headline_text] = headline_link

        if 'northumberlandgazette.co.uk' in url:
            for article in soup.find_all('a', class_='article-title'):
                headline_text = article.text
                headline_link = 'https://www.northumberlandgazette.co.uk' + article['href']
                all_headlines_links[headline_text] = headline_link

        if 'sunderlandecho.com' in url:
            for article in soup.find_all('a', class_='article-title'):
                headline_text = article.text
                headline_link = 'https://www.sunderlandecho.com' + article['href']
                all_headlines_links[headline_text] = headline_link

        if 'worcesternews.co.uk' in url:
            # Get hero item
            for article in soup.find_all('a', class_='mar-lead-story__link'):
                headline_text = article.find('span').text
                headline_link = 'https://www.worcesternews.co.uk' + article['href']
                if 'lott' in headline_text.lower() or 'forecast' in headline_text.lower() or 'live:' in headline_text.lower() or '-live-' in headline_link:
                    continue
                all_headlines_links[headline_text] = headline_link

            for article in soup.find_all('a', class_='text-slate no-underline'):
                headline_text = article.text
                headline_link = 'https://www.worcesternews.co.uk' + article['href']
                if 'lott' in headline_text.lower() or 'forecast' in headline_text.lower() or 'live:' in headline_text.lower() or '-live-' in headline_link:
                    continue
                all_headlines_links[headline_text] = headline_link

        if 'worcesterobserver.co.uk' in url:
            for article in soup.find_all('a', class_='box_link'):
                headline_text = article.find(class_='box_title').text
                headline_link = article['href']
                all_headlines_links[headline_text] = headline_link


    return all_headlines_links


def get_urls(headlines, headlines_links):
    # Remove backslashes from headlines
    headlines = [headline.replace('\\', '') for headline in headlines]

    urls = []
    for headline in headlines:
        # print('HEADLINE IN SCRAPE ARTICLES')
        # print(headline)
        for key, value in headlines_links.items():
            if headline in key:
                urls.append(value)

    if len(urls) == 0:
        raise Exception('URL list empty. Could not locate headlines in dictionary of links.')
    
    return urls


def scrape_articles(headlines, headlines_links):
    print(headlines)

    urls = get_urls(headlines, headlines_links)

    print('URLS')
    print(urls)

    articles = []

    for url in urls:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        temp_article = ""

        try:
            if 'telegraph.co.uk' in url:
                article_div = soup.find("div", {"data-js": "article-body"})
                for p in article_div.find_all("p"):
                    text = p.get_text()
                    temp_article += "\n\n" + text

            if 'bbc.co.uk' in url:
                text_block_divs = soup.find_all("div", {"data-component": "text-block"})
                for div in text_block_divs:
                    p = div.find("p")
                    text = p.get_text()
                    temp_article += "\n\n" + text

            if 'washingtonpost.com' in url:
                for div in soup.find_all("div", class_="article-body"):
                    for p in div.find_all("p"):
                        text = p.get_text()
                        if "Sign up to get the rest free, including news from around the globe and interesting ideas and opinions to know, sent to your inbox every weekday." in text:
                            continue
                        temp_article += "\n\n" + text

            if 'theguardian.com' in url:
                article_div = soup.find("div", class_='article-body-commercial-selector')
                for p in article_div.find_all('p'):
                    text = p.get_text()
                    temp_article += "\n\n" + text

            if 'independent.co.uk' in url:
                article_div = soup.find('div', id='main')
                for p in article_div.find_all('p'):
                    text = p.get_text()
                    temp_article += "\n\n" + text

            if 'newscientist.com' in url:
                article_div = soup.find('div', class_='article__content')
                for p in article_div.find_all('p'):
                    text = p.get_text()
                    if "Read more" in text or 'Journal reference' in text or 'More on these topics' in text:
                            continue
                    temp_article += "\n\n" + text

            if 'scitechdaily.com' in url:
                article_div = soup.find('div', class_='entry-content clearfix')
                for p in article_div.find_all('p'):
                    text = p.get_text()
                    if "Reference:" in text:
                            continue
                    temp_article += "\n\n" + text

            if 'reuters.com' in url:
                article_div = soup.find('div', class_='article-body__content__17Yit')
                for p in article_div.find_all('p'):
                    text = p.get_text()
                    if "Our Standards:" in text:
                            continue
                    temp_article += "\n\n" + text

            if 'apnews.com' in url:
                article_div = soup.find('div', class_='Article')
                for p in article_div.find_all('p'):
                    text = p.get_text()
                    if "This article was published" in text or '___' in text:
                            continue
                    temp_article += "\n\n" + text

            if 'news.sky.com' in url:
                article_div = soup.find('div', class_='sdc-article-body')
                for p in article_div.find_all('p'):
                    text = p.get_text()
                    if "Read more" in text or 'Please use Chrome browser' in text or 'Click to subscribe' in text:
                            continue
                    temp_article += "\n\n" + text

            if 'eu.usatoday.com' in url:
                article_div = soup.find('article', class_='primary-content')
                for p in article_div.find_all('p'):
                    text = p.get_text()
                    if "Read more" in text or 'Please use Chrome browser' in text or 'Click to subscribe' in text:
                            continue
                    temp_article += "\n\n" + text

            if 'gazettelive.co.uk' in url:
                article_div = soup.find('div', class_='article-body')
                for p in article_div.find_all('p', recursive=False):
                    text = p.get_text()
                    if "READ" in text:
                        continue
                    temp_article += "\n\n" + text

            if 'thenorthernecho.co.uk' in url:
                # Get first paragraph
                first_para = soup.find('p', class_='article-first-paragraph').get_text()
                temp_article += '\n\n' + first_para

                article_div = soup.find('div', id='subscription-content')
                for p in article_div.find_all('p', recursive=False):
                    text = p.get_text()
                    if "Read next" in text or 'Read more' in text or 'To get more stories direct' in text or 'Get more from The Northern Echo' in text:
                        continue
                    temp_article += '\n\n' + text

            if 'chroniclelive.co.uk' in url:
                article_div = soup.find('div', class_='article-body')
                for p in article_div.find_all('p'):
                    text = p.get_text()
                    if "Read more" in text:
                        continue
                    temp_article += '\n\n' + text
            
            if 'shieldsgazette.com' in url:
                article_div = soup.find('div', class_='article-content')
                for p in article_div.find_all('p'):
                    text = p.get_text()
                    if "Read South" in text:
                        continue
                    temp_article += '\n\n' + text

            if 'northumberlandgazette.co.uk' in url:
                article_div = soup.find('div', class_='article-content')
                for p in article_div.find_all('p'):
                    text = p.get_text()
                    temp_article += '\n\n' + text

            if 'sunderlandecho.com' in url:
                article_div = soup.find('div', class_='article-content')
                for p in article_div.find_all('p'):
                    text = p.get_text()
                    temp_article += '\n\n' + text

            if 'worcesternews.co.uk' in url:
                article_div = soup.find('div', class_='article-body')
                for p in article_div.find_all('p'):
                    text = p.get_text()
                    temp_article += '\n\n' + text
                
            if 'worcesterobserver.co.uk' in url:
                article_div = soup.find('div', class_='np-article')
                for p in article_div.find_all('p'):
                    text = p.get_text()
                    temp_article += '\n\n' + text

            articles.append(temp_article)
        except:
            pass

    for article in articles:
        if article == '':
            articles.remove(article)

    if articles == []:
        from app import mark_covered
        mark_covered(headlines)
        raise Exception('No articles found. Could not locate article text in dictionary of links.')

    return articles


def get_article_images(urls):
    imgs = []
    for url in urls:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        if 'newsnotfound.com' in url:
            img = soup.find('img', class_='attachment-post-thumbnail')
            imgs.append(img.get('src'))
    return imgs
