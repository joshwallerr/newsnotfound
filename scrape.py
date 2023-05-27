import requests
from bs4 import BeautifulSoup
from requests_html import HTMLSession


def headlines_links(urls):
    """
    This function scrapes headlines and links from various news websites and returns
    them in a dictionary.
    """
    all_headlines_links = {}

    for url in urls:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.text, 'html.parser')

        if 'telegraph.co.uk' in url:
            for headline in soup.find_all('a', class_='list-headline__link u-clickable-area__link'):
                headline_text = headline.find('span', class_='list-headline__text').find('span').text
                headline_link = 'https://www.telegraph.co.uk' + headline.get('href')
                all_headlines_links[headline_text] = headline_link

        if 'bbc.co.uk' in url:
            for article in soup.find_all('div', class_='gs-c-promo-body'):
                headline = article.find('h3')
                headline_text = headline.text
                headline_link = article.find('a')['href']
                video = article.find('span', class_='qa-offscreen gs-u-vh')
                if video:
                    continue
                if headline_link[0] == '/':
                    headline_link = 'https://www.bbc.co.uk' + headline_link
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
                if '/live/' in headline_link.lower() or 'first thing:' in headline_text.lower():
                    continue
                all_headlines_links[headline_text] = headline_link

        if 'independent.co.uk' in url:
            loop_count = 0
            for article in soup.find_all('a', class_='title'):
                if loop_count > 16:
                    break
                headline_text = article.text
                headline_link = 'https://www.independent.co.uk' + article['href']
                all_headlines_links[headline_text] = headline_link
                loop_count += 1

        if 'newscientist.com' in url:
            for article in soup.find_all('a', class_='CardLink'):
                headline_text = article.find('h3', class_='Card__Title').text
                headline_link = article['href']
                if headline_link[0] == '/':
                    headline_link = 'https://www.newscientist.com' + headline_link
                all_headlines_links[headline_text] = headline_link

        if 'scitechdaily.com' in url:
            for article in soup.find_all('h3', class_='entry-title'):
                headline = article.find('a')
                headline_text = headline.text
                headline_link = headline['href']
                all_headlines_links[headline_text] = headline_link

        if 'reuters.com' in url and '/archive/' not in url and '/markets/' not in url:
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
            try:
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
            except:
                continue

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
                if '/sport/' in headline_link:
                    continue
                all_headlines_links[headline_text] = headline_link

        if 'thenorthernecho.co.uk' in url:
            # Get hero item
            for article in soup.find_all('a', class_='mar-lead-story__link'):
                headline_text = article.find('span').text
                headline_link = 'https://www.thenorthernecho.co.uk' + article['href']
                if 'lott' in headline_text.lower() or 'forecast' in headline_text.lower() or 'live:' in headline_text.lower() or '-live-' in headline_link or '/sport/' in headline_link:
                    continue
                all_headlines_links[headline_text] = headline_link

            for article in soup.find_all('a', class_='text-slate no-underline'):
                headline_text = article.text
                headline_link = 'https://www.thenorthernecho.co.uk' + article['href']
                if 'lott' in headline_text.lower() or 'forecast' in headline_text.lower() or 'live:' in headline_text.lower() or '-live-' in headline_link or '/sport/' in headline_link:
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

        if 'bedfordindependent.co.uk' in url:
            for article in soup.find_all('h3', class_='entry-title td-module-title'):
                headline_text = article.find('a').text
                headline_link = article.find('a')['href']
                all_headlines_links[headline_text] = headline_link

        if 'bedfordshirelive.co.uk' in url:
            for article in soup.find_all('a', class_="headline"):
                headline_text = article.text
                headline_link = article['href']
                all_headlines_links[headline_text] = headline_link

        if 'eveningnews24.co.uk' in url:
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

        if 'examinerlive.co.uk' in url:
            for article in soup.find_all('a', class_="headline"):
                headline_text = article.text
                headline_link = article['href']
                all_headlines_links[headline_text] = headline_link

        if 'plymouthherald.co.uk' in url:
            for article in soup.find_all('a', class_="headline"):
                headline_text = article.text
                headline_link = article['href']
                all_headlines_links[headline_text] = headline_link

        if 'thehindu.com' in url:
            for article in soup.find_all('h3', class_="title"):
                headline_text = article.find('a').text
                headline_link = article.find('a')['href']
                all_headlines_links[headline_text] = headline_link

        if 'indianexpress.com' in url:
            for article in soup.find_all('h2', class_="title"):
                headline_text = article.find('a').text
                headline_link = article.find('a')['href']
                all_headlines_links[headline_text] = headline_link

        if 'aljazeera.com' in url:
            for article in soup.find_all('a', class_="u-clickable-card__link"):
                headline_text = article.find('span').text
                headline_link = 'https://www.aljazeera.com' + article['href']
                all_headlines_links[headline_text] = headline_link

        if 'reuters.com' in url and '/archive/' in url and '/markets/' not in url:
            article_div = soup.find('div', class_="column1")
            for article in article_div.find_all('div', class_="story-content"):
                headline_text = article.find('h3').text
                headline_link = 'https://www.reuters.com' + article.find('a')['href']
                all_headlines_links[headline_text] = headline_link

        # if 'reuters.com' in url and '/archive/' not in url and '/markets/' in url:
        #     article_div = soup.find('div', class_="column1")
        #     for article in article_div.find_all('div', class_="story-content"):
        #         headline_text = article.find('h3').text
        #         headline_link = 'https://www.reuters.com' + article.find('a')['href']
        #         all_headlines_links[headline_text] = headline_link

        if 'brazilian.report' in url:
            article_div = soup.find('div', class_="col-main")
            for article in article_div.find_all('div', class_="news-card"):
                headline_text = article.find('h3').text
                headline_link = article.find('a')['href']
                all_headlines_links[headline_text] = headline_link

        if 'folha.uol.com.br' in url:
            # Get hero item
            for article in soup.find_all('a', class_='c-main-headline__wrapper'):
                headline_text = article.find('h2').text
                headline_link = article.find('a', class_='c-main-headline__url')['href']
                all_headlines_links[headline_text] = headline_link

            loop_count = 0
            for article in soup.find_all('div', class_="c-headline__content"):
                if loop_count > 16:
                    break
                headline_text = article.find('h2').text
                headline_link = article.find('a')['href']
                all_headlines_links[headline_text] = headline_link
                loop_count += 1

        if 'huffingtonpost.co.uk' in url:
            for article in soup.find_all('div', class_="card__headlines"):
                headline_text = article.find('h3').text
                headline_link = article.find('a')['href']
                all_headlines_links[headline_text] = headline_link

        if 'ft.com' in url:
            news_div = soup.find('ul', class_="o-teaser-collection__list js-stream-list")
            for article in news_div.find_all('li', class_="o-teaser-collection__item o-grid-row"):
                headline_text = article.find('a', class_='js-teaser-heading-link')
                if headline_text is None:
                    continue
                headline_text = headline_text.text
                headline_link = 'https://www.ft.com' + article.find('a', class_='js-teaser-heading-link')['href']
                all_headlines_links[headline_text] = headline_link

        if 'yahoo.com' in url and '/topics/' in url:
            for article in soup.find_all('a', class_="stream-title"):
                headline_text = article.text
                headline_link = article['href']
                if headline_link[0] == '/':
                    headline_link = 'https://www.yahoo.com' + headline_link
                all_headlines_links[headline_text] = headline_link

        if 'yahoo.com' in url and '/topics/' not in url:
            for article in soup.find_all('a', class_="mega-item-header-link"):
                headline_text = article.text
                headline_link = article['href']
                if headline_link[0] == '/':
                    headline_link = 'https://www.yahoo.com' + headline_link
                all_headlines_links[headline_text] = headline_link
            
        if 'standard.co.uk' in url:
            for article in soup.find_all('a', class_="title"):
                headline_text = article.text
                headline_link = article['href']
                if headline_link[0] == '/':
                    headline_link = 'https://www.standard.co.uk' + headline_link
                all_headlines_links[headline_text] = headline_link

        if 'businessgreen.com' in url:
            article_div = soup.find('div', class_="platformheading")
            for article in soup.find_all('a', class_="lock"):
                headline_text = article.text
                headline_link = article['href']
                if headline_link[0] == '/':
                    headline_link = 'https://www.businessgreen.com' + headline_link
                all_headlines_links[headline_text] = headline_link

        if 'solarpowerportal.co.uk' in url:
            for article in soup.find_all('h2', class_="article-list__title"):
                headline_text = article.find('a').text
                headline_link = article.find('a')['href']
                if headline_link[0] == '/':
                    headline_link = 'https://www.solarpowerportal.co.uk' + headline_link
                all_headlines_links[headline_text] = headline_link

        if 'pv-magazine.com' in url:
            for article in soup.find_all('h2', class_="entry-title"):
                headline_text = article.find('a').text
                headline_link = article.find('a')['href']
                if headline_link[0] == '/':
                    headline_link = 'https://www.pv-magazine.com' + headline_link
                all_headlines_links[headline_text] = headline_link

        if 'solarpowerworldonline.com' in url:
            for article in soup.find_all('h2', class_="entry-title"):
                headline_text = article.find('a').text
                headline_link = article.find('a')['href']
                if headline_link[0] == '/':
                    headline_link = 'https://www.solarpowerworldonline.com' + headline_link
                all_headlines_links[headline_text] = headline_link

        if 'rechargenews.com' in url:
            for article in soup.find_all('a', class_="card-link text-reset"):
                headline_text = article.text
                headline_link = article['href']
                if headline_link[0] == '/':
                    headline_link = 'https://www.rechargenews.com' + headline_link
                all_headlines_links[headline_text] = headline_link

        if 'offshorewind.biz' in url:
            for article in soup.find_all('a', class_="card__link"):
                headline_text = article.text
                headline_link = article['href']
                if headline_link[0] == '/':
                    headline_link = 'https://www.offshorewind.biz' + headline_link
                all_headlines_links[headline_text] = headline_link

        if 'windpowermonthly.com' in url:
            for article in soup.find_all('p', class_="articleLink"):
                headline_text = article.find('a').text
                headline_link = article.find('a')['href']
                if headline_link[0] == '/':
                    headline_link = 'https://www.windpowermonthly.com' + headline_link
                all_headlines_links[headline_text] = headline_link

        if 'www.gasworld.com' in url:
            for article in soup.find_all('h3', class_="story-list-article--title"):
                headline_text = article.find('a').text
                headline_link = article.find('a')['href']
                if headline_link[0] == '/':
                    headline_link = 'https://www.gasworld.com' + headline_link
                all_headlines_links[headline_text] = headline_link

        if 'naturalgasworld.com' in url:
            for span in soup.find_all('span', class_="ribbon complimentary"):
                article = span.find_parents('article')[0]  # [0] to get the first (and in this case, the only) matching ancestor
                headline = article.find('h2', class_="u-ttu")
                if headline:
                    headline_text = headline.find('a').text
                    headline_link = headline.find('a')['href']
                    if headline_link[0] == '/':
                        headline_link = 'https://www.naturalgasworld.com' + headline_link
                    all_headlines_links[headline_text] = headline_link
            
        if 'h2-view.com' in url:
            for article in soup.find_all('h3', class_="story-list-article--title"):
                headline_text = article.find('a').text
                headline_link = article.find('a')['href']
                if headline_link[0] == '/':
                    headline_link = 'https://www.h2-view.com' + headline_link
                all_headlines_links[headline_text] = headline_link

        if 'hydrogeninsight.com' in url:
            for article in soup.find_all('a', class_="card-link text-reset"):
                headline_text = article.text
                headline_link = article['href']
                if headline_link[0] == '/':
                    headline_link = 'https://www.hydrogeninsight.com' + headline_link
                all_headlines_links[headline_text] = headline_link

        if 'investing.com' in url:
            session = HTMLSession()
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
            }
            response = session.get(url, headers=headers)
            response.html.render()

            article_div = response.html.find('div.largeTitle', first=True)
            for article in article_div.find('a.title'):
                headline_text = article.text
                headline_link = article.attrs['href']
                if 'invst.ly' in headline_link:
                    continue
                if headline_link[0] == '/':
                    headline_link = 'https://uk.investing.com' + headline_link
                all_headlines_links[headline_text] = headline_link

        if 'spglobal.com' in url:
            for article in soup.find_all('div', class_="newsId"):
                headline_text = article.find('h2').text
                headline_link = article.find('a')['href']
                if 'plattsinfo' in headline_link:
                    continue
                if headline_link[0] == '/':
                    headline_link = 'https://www.spglobal.com' + headline_link
                all_headlines_links[headline_text] = headline_link

        if 'fxstreet.com' in url:
            session = HTMLSession()
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
            }
            response = session.get(url, headers=headers)
            response.html.render()

            for article in response.html.find('h4.fxs_headline_tiny'):
                headline_text = article.find('a', first=True).text
                headline_link = article.find('a', first=True).attrs['href']
                if headline_link[0] == '/':
                    headline_link = 'https://www.fxstreet.com' + headline_link
                all_headlines_links[headline_text] = headline_link

        if 'metalsdaily.com' in url:
            for article in soup.find_all('div', class_="newsTable ns_NewsTable"):
                headline_text = article.find('span', class_="Title").text
                headline_link = article.find('a', class_="NewsItem")['href']
                if headline_link[0] == '/':
                    headline_link = 'https://www.metalsdaily.com' + headline_link
                all_headlines_links[headline_text] = headline_link
        
        if 'kitco.com' in url:
            for article in soup.find_all('a', class_="newslink"):
                headline_text = article.text
                headline_link = article['href']
                if headline_link[0] == '/':
                    headline_link = 'https://www.kitco.com' + headline_link
                all_headlines_links[headline_text] = headline_link

        if 'farminguk.com' in url:
            for article in soup.find_all('h4', class_="post-title"):
                headline_text = article.find('a').text
                headline_link = article.find('a')['href']
                if headline_link[0] == '/':
                    headline_link = 'https://www.farminguk.com' + headline_link
                all_headlines_links[headline_text] = headline_link

        if 'fwi.co.uk' in url:
            for article in soup.find_all('div', class_="card-info"):
                for child in article.children:
                    if child.name == 'a':
                        headline_text = child.find('h2').text
                        headline_link = child['href']
                        if headline_link[0] == '/':
                            headline_link = 'https://www.fwi.co.uk' + headline_link
                        all_headlines_links[headline_text] = headline_link

        if 'agriland.co.uk' in url:
            for article in soup.find_all('div', class_="article"):
                headline_text = article.find('h4').text
                headline_link = article.find('a')['href']
                if headline_link[0] == '/':
                    headline_link = 'https://www.agriland.co.uk' + headline_link
                all_headlines_links[headline_text] = headline_link

        try:
            if 'agdaily.com' in url:
                article_div = soup.find('section', class_="col-sm-8 list_posts")
                for article in article_div.find_all('header'):
                    h1 = article.find('h1')
                    headline_text = h1.find('a').text
                    headline_link = h1.find('a')['href']
                    if headline_link[0] == '/':
                        headline_link = 'https://www.agdaily.com' + headline_link
                    all_headlines_links[headline_text] = headline_link
        except:
            continue

        # if 'agriculture.com' in url:
        #     for article in article_div.find_all('span', class_="field-content"):
        #         print('article')
        #         headline_text = article.find('a').text
        #         headline_link = article.find('a')['href']
        #         if headline_link[0] == '/':
        #             headline_link = 'https://www.agriculture.com' + headline_link
        #         all_headlines_links[headline_text] = headline_link

        if 'agweb.com' in url:
            loop_count = 0
            for article in soup.find_all('a', class_="field--name-title"):
                if loop_count > 14:
                    break
                headline_text = article.text
                headline_link = article['href']
                if headline_link[0] == '/':
                    headline_link = 'https://www.agweb.com' + headline_link
                all_headlines_links[headline_text] = headline_link
                loop_count += 1

        # add loop up to 16 times
        if 'farmprogress.com' in url:
            loop_count = 0
            article_div = soup.find('div', class_="ListContent-Body")
            for article in article_div.find_all('a', {"data-testid": "preview-default-title"}):
                if loop_count > 16:
                    break
                headline_text = article.text
                headline_link = article['href']
                if headline_link[0] == '/':
                    headline_link = 'https://www.farmprogress.com' + headline_link
                all_headlines_links[headline_text] = headline_link
                loop_count += 1

        if 'cryptonews.com' in url:
            article_div = soup.find('div', class_="row", id="load_more_target")
            for article in article_div.find_all('a', class_="article__title article__title--md article__title--featured"):
                headline_text = article.find('h4').text
                headline_link = article['href']
                if headline_link[0] == '/':
                    headline_link = 'https://www.cryptonews.com' + headline_link
                if 'price analysis' in headline_text.lower() or 'recap' in headline_text.lower():
                    continue
                all_headlines_links[headline_text] = headline_link

        if 'cryptonews.net' in url:
            article_div = soup.find('section', class_="col-xs-12 col-sm")
            for article in article_div.find_all('a', class_="title"):
                headline_text = article.text
                headline_link = article['href']
                if headline_link[0] == '/':
                    headline_link = 'https://www.cryptonews.net' + headline_link
                if 'price analysis' in headline_text.lower() or 'recap' in headline_text.lower():
                    continue
                all_headlines_links[headline_text] = headline_link

        if 'cryptopotato.com' in url:
            loop_count = 0
            article_div = soup.find('section', id="main")
            for article in article_div.find_all('h3', class_="rpwe-title"):
                if loop_count > 16:
                    break
                headline_text = article.find('a').text
                headline_link = article.find('a')['href']
                if headline_link[0] == '/':
                    headline_link = 'https://www.cryptopotato.com' + headline_link
                if 'price analysis' in headline_text.lower() or 'recap' in headline_text.lower():
                    continue
                all_headlines_links[headline_text] = headline_link
                loop_count += 1

    return all_headlines_links


def get_urls(headlines, headlines_links):
    """
    This function takes in a list of headlines and a dictionary of headline and links, removes backslashes
    from the headlines, and returns a list of URLs corresponding to the headlines found in the
    dictionary.
    """
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
    """
    This function scrapes articles from various news websites based on the provided headlines and their
    corresponding links.
    """
    print(headlines)

    urls = get_urls(headlines, headlines_links)

    print('URLS')
    print(urls)

    articles = []

    for url in urls:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
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
                    if 'click here' in text.lower() or '':
                        continue
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
                article_div = soup.find('section', class_='ArticleContent zephr-article-content')
                for p in article_div.find_all('p'):
                    if not p.attrs:
                        text = p.get_text()
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

            if 'bedfordindependent.co.uk' in url:
                article_div = soup.find('div', class_='td-post-content')
                for p in article_div.find_all('p'):
                    text = p.get_text()
                    temp_article += '\n\n' + text

            if 'bedfordshirelive.co.uk' in url:
                article_div = soup.find('div', class_='article-body')
                for p in article_div.find_all('p', recursive=False):
                    text = p.get_text()
                    if "READ" in text:
                        continue
                    temp_article += "\n\n" + text

            if 'eveningnews24.co.uk' in url:
                article_div = soup.find('div', class_='article-body')
                for p in article_div.find_all('p'):
                    text = p.get_text()
                    temp_article += '\n\n' + text

            if 'examinerlive.co.uk' in url:
                article_div = soup.find('div', class_='article-body')
                for p in article_div.find_all('p', recursive=False):
                    text = p.get_text()
                    if "read more" in text.lower() or "read next" in text.lower():
                        continue
                    temp_article += "\n\n" + text

            if 'plymouthherald.co.uk' in url:
                article_div = soup.find('div', class_='article-body')
                for p in article_div.find_all('p', recursive=False):
                    text = p.get_text()
                    if "read more" in text.lower() or "read next" in text.lower():
                        continue
                    temp_article += "\n\n" + text

            if 'thehindu.com' in url:
                article_div = soup.find('div', class_='articlebodycontent')
                for p in article_div.find_all('p'):
                    if p.get('class') is None:
                        text = p.get_text()
                        if 'also read: ' in text.lower():
                            continue
                        temp_article += '\n\n' + text

            if 'indianexpress.com' in url:
                article_div = soup.find('div', id='pcl-full-content')
                for p in article_div.find_all('p'):
                    text = p.get_text()
                    temp_article += '\n\n' + text

            if 'aljazeera.com' in url:
                article_div = soup.find('main', id='main-content-area')
                for p in article_div.find_all('p'):
                    text = p.get_text()
                    temp_article += '\n\n' + text

            if 'folha.uol.com.br' in url:
                article_div = soup.find('div', class_='c-news__body')
                for p in article_div.find_all('p'):
                    text = p.get_text()
                    if 'translated by' in text.lower() or 'read the article in the original language' in text.lower():
                        continue
                    temp_article += '\n\n' + text

            if 'huffingtonpost.co.uk' in url:
                article_div = soup.find('section', class_='entry__content-list js-entry-content js-cet-subunit')
                for p in article_div.find_all('div', class_='primary-cli'):
                    text = p.get_text()
                    temp_article += '\n\n' + text

            if 'ft.com' in url:
                print(soup)
                article_div = soup.find('div', class_='article__content-body n-content-body js-article__content-body')
                for p in article_div.find_all('p'):
                    text = p.get_text()
                    temp_article += '\n\n' + text

            if 'yahoo.com' in url:
                article_div = soup.find('div', class_='caas-body')
                for p in article_div.find_all('p'):
                    text = p.get_text()
                    if '(reporting by' in text.lower():
                        continue
                    temp_article += '\n\n' + text
            
            if 'standard.co.uk' in url:
                article_div = soup.find('div', id='main')
                for p in article_div.find_all('p'):
                    text = p.get_text()
                    temp_article += '\n\n' + text

            if 'businessgreen.com' in url:
                article_div = soup.find('div', class_='article-body')
                for p in article_div.find_all('p'):
                    text = p.get_text()
                    temp_article += '\n\n' + text

            if 'solarpowerportal.co.uk' in url:
                article_div = soup.find('div', class_='article__body')
                for p in article_div.find_all('p'):
                    text = p.get_text()
                    if 'solar power portal' in text.lower() or 'solar summit' in text.lower() or 'image:' in text.lower():
                        continue
                    temp_article += '\n\n' + text

            if 'pv-magazine.com' in url:
                article_div = soup.find('div', class_='entry-content')
                for p in article_div.find_all('p'):
                    text = p.get_text()
                    if 'pv magazine' in text.lower() or 'to continue reading' in text.lower() or 'image:' in text.lower() or 'pv-magazine' in text.lower():
                        continue
                    temp_article += '\n\n' + text

            if 'solarpowerworldonline.com' in url:
                article_div = soup.find('div', class_='entry-content')
                for p in article_div.find_all('p'):
                    text = p.get_text()
                    temp_article += '\n\n' + text

            if 'rechargenews.com' in url:
                article_div = soup.find('div', class_='article-body')
                for p in article_div.find_all('p'):
                    text = p.get_text()
                    temp_article += '\n\n' + text
            
            if 'offshorewind.biz' in url:
                article_div = soup.find('div', class_='wp-content')
                for element in article_div.children:
                    if element.name == 'p':
                        text = element.get_text()
                        temp_article += '\n\n' + text
                    elif element.name == 'div' and 'section' in element.get('class', []):
                        break

            if 'windpowermonthly.com' in url:
                article_div = soup.find('div', class_='ArticleBodyPaywall')
                for p in article_div.find_all('p'):
                    text = p.get_text()
                    temp_article += '\n\n' + text

            if 'www.gasworld.com' in url:
                article_div = soup.find('div', class_='article-content')
                for p in article_div.find_all('p'):
                    text = p.get_text()
                    if 'read more:' in text.lower():
                        continue
                    temp_article += '\n\n' + text

            if 'naturalgasworld.com' in url:
                article_div = soup.find('article', class_='content full')
                for child in article_div.children:
                    if child.name == 'p':
                        text = child.get_text()
                        temp_article += '\n\n' + text

            if 'h2-view.com' in url:
                article_div = soup.find('div', class_='article-content')
                for child in article_div.children:
                    if child.name == 'p':
                        text = child.get_text()
                        temp_article += '\n\n' + text

            if 'hydrogeninsight.com' in url:
                article_div = soup.find('div', class_='article-body')
                for p in article_div.find_all('p'):
                    text = p.get_text()
                    temp_article += '\n\n' + text

            if 'investing.com' in url:
                session = HTMLSession()
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
                }
                response = session.get(url, headers=headers)
                response.html.render()

                article_div = response.html.find('div.articlePage', first=True)
                for p in article_div.find('p'):
                    text = p.text
                    temp_article += '\n\n' + text

            if 'spglobal.com' in url:
                article_div = soup.find('div', class_='article__content')
                for p in article_div.find_all('p'):
                    text = p.get_text()
                    temp_article += '\n\n' + text

            if 'fxstreet.com' in url:
                article_div = soup.find('div', class_='fxs_article_content')
                for child in article_div.children:
                    if child.name == 'p':
                        text = child.get_text()
                        temp_article += '\n\n' + text

            if 'kitco.com' in url:
                article_div = soup.find('article', {"itemprop": "articleBody"})
                for child in article_div.children:
                    if child.name == 'p':
                        text = child.get_text()
                        temp_article += '\n\n' + text

            if 'farminguk.com' in url:
                article_div = soup.find('div', class_='news-content')
                for child in article_div.children:
                    if child.name == 'p':
                        text = child.get_text()
                        temp_article += '\n\n' + text

            if 'fwi.co.uk' in url:
                article_div = soup.find('div', class_='article-body')
                for child in article_div.children:
                    if child.name == 'p':
                        text = child.get_text()
                        temp_article += '\n\n' + text

            if 'agriland.co.uk' in url:
                article_div = soup.find('main', class_='article-body')
                for child in article_div.children:
                    if child.name == 'p':
                        text = child.get_text()
                        temp_article += '\n\n' + text

            if 'agweb.com' in url:
                article_div = soup.find('div', class_='field--name-body')
                for child in article_div.children:
                    if child.name == 'p':
                        text = child.get_text()
                        if 'agritalk' in text.lower() or 'related story:' in text.lower():
                            continue
                        temp_article += '\n\n' + text

            if 'agdaily.com' in url:
                article_div = soup.find('div', class_='col-sm-8 article-content')
                real_div = article_div.find_all('div')[0]
                for child in real_div.children:
                    if child.name == 'p':
                        text = child.get_text()
                        if 'related:' in text.lower():
                            continue
                        temp_article += '\n\n' + text

            if 'farmprogress.com' in url:
                article_div = soup.find('div', class_='ContentModule-Wrapper')
                for child in article_div.children:
                    if child.name == 'p':
                        text = child.get_text()
                        if 'you may also like' in text.lower():
                            continue
                        temp_article += '\n\n' + text

            if 'cryptonews.com' in url:
                article_div = soup.find('div', class_='article-single__content category_contents_details')
                for child in article_div.children:
                    if child.name == 'p':
                        text = child.get_text()
                        temp_article += '\n\n' + text

            if 'cryptonews.net' in url:
                article_div = soup.find('div', class_='news-item detail content_text')
                for child in article_div.children:
                    if child.name == 'p':
                        text = child.get_text()
                        temp_article += '\n\n' + text

            if 'cryptopotato.com' in url:
                article_div = soup.find('div', class_='coincodex-content')
                for p in article_div.find_all('p'):
                    text = p.get_text()
                    temp_article += '\n\n' + text

                for li in article_div.find_all('li'):
                    if 'rp4wp-col' not in li.get('class', []):
                        text = li.get_text()
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
    """
    This function takes a list of URLs, scrapes each URL for images, and returns a list of image URLs
    for articles on a specific website.
    """
    imgs = []
    for url in urls:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        if 'newsnotfound.com' in url:
            img = soup.find('img', class_='attachment-post-thumbnail')
            imgs.append(img.get('src'))
    return imgs
