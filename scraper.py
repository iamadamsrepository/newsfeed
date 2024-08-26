from abc import ABC, abstractmethod
from typing import Dict, List
import unicodedata
import requests
import json
import html
from bs4 import BeautifulSoup

from db.db_connection import DBHandler
from rss import RSSFeeds

FEED_URLS = {
    "ABCUS Top": "https://abcnews.go.com/abcnews/topstories",
    # "WSJ World": "https://feeds.a.dj.com/rss/RSSWorldNews.xml",
    "CBS World": "https://www.cbsnews.com/latest/rss/world",
    "GRD World": "https://www.theguardian.com/world/rss",
    # "NYT World": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "BBC World": "http://feeds.bbci.co.uk/news/world/rss.xml",
    # "CNN World": "http://rss.cnn.com/rss/edition_world.rss",
    "SMH World": "https://www.smh.com.au/rss/world.xml",
    "SBS World": "https://www.sbs.com.au/news/topic/world/feed",
}

class Scraper(ABC):
    @classmethod
    @abstractmethod
    def article_text(url: str) -> str:
        ...

class SBSScraper(Scraper):
    #TODO Key points

    split_before = """<script type="application/ld+json" data-testid="product-jsonld">"""
    split_after = "</script>"

    @classmethod
    def article_text(cls, url: str) -> str:
        html_str: str = requests.get(url).text
        json_str: str = html_str.split(cls.split_before)[1].split(cls.split_after)[0]
        json_obj: dict = json.loads(json_str)
        html_article_text: str = json_obj['@graph'][1]['articleBody']
        article_text: str = html.unescape(html_article_text.replace('&amp;', '&'))
        return article_text
    

class SMHScraper(Scraper):

    split_before = "<script>window.INITIAL_STATE = JSON.parse(\""
    split_after = "\");</script>"

    @classmethod
    def article_text(cls, url: str) -> str:
        html_str: str = requests.get(url).text
        json_str: str = html_str.split(cls.split_before)[1].split(cls.split_after)[0]
        json_str = ''.join([i.split("</x-placeholder>")[-1] for i in json_str.split("<x-placeholder")])
        json_obj: dict = json.loads(json_str.replace('\\"', '"').replace('\\\\"', '\\"'))
        html_article_obj: str = list(json_obj['page'].values())[0]['asset']['asset']
        if 'body' not in html_article_obj:
            return None
        html_article_text = html_article_obj['body']
        article_text: str = html.unescape(BeautifulSoup(html_article_text.replace('</p><p>', ' ').replace('. .', '.'), 'lxml').text).encode().decode('unicode-escape')
        return article_text
    

class CNNScraper(Scraper):

    split_before = """<script type="application/ld+json">"""
    split_after = "</script>"

    @classmethod
    def article_text(cls, url: str) -> str:
        if 'live-news' in url:
            return None
        html_str: str = requests.get(url).text
        json_str: str = html_str.split(cls.split_before)[1].split(cls.split_after)[0]
        json_obj: dict = json.loads(json_str)
        article_text: str = json_obj['articleBody']
        return article_text


class BBCScraper(Scraper):

    split_before = 'window.__INITIAL_DATA__="'
    split_after = '";</script>'
    split_before2 = """<script id="__NEXT_DATA__" type="application/json">"""
    split_after2 = "</script>"

    @classmethod
    def article_text(cls, url: str) -> str:
        if '/news/live/' in url:
            return None
        html_str: str = requests.get(url).text
        try:
            json_str: str = html_str.split(cls.split_before)[1].split(cls.split_after)[0]
            json_obj: dict = json.loads(json_str.replace('\\"', '"').replace('\\\\', '\\'))
            return cls.type1(json_obj)
        except:
            json_str: str = html_str.split(cls.split_before2)[1].split(cls.split_after2)[0]
            json_obj: dict = json.loads(json_str)
            return cls.type2(json_obj)
        
    @classmethod
    def type1(cls, json_obj: dict) -> str:
        try:
            blocks: List[dict] = [i for i in json_obj['stores']['article']['articleBodyContent'] if i['type'] == 'text']
        except KeyError:
            return None
        blocks = [i['model']['blocks'][0]['model']['text'] for i in blocks]
        article_text: str = ' '.join(blocks).replace('\\', '')
        return article_text
    
    @classmethod
    def type2(cls, json_obj: dict) -> str:
        blocks: List[dict] = [i for i in list(json_obj['props']['pageProps']['page'].values())[0]['contents'] if i['type'] == 'text']
        article_text: str = ' '.join([i['model']['text'] for i in filter(lambda a: a['type'] == 'paragraph', sum([i['model']['blocks'] for i in blocks], []))])
        return article_text


class NYTScraper(Scraper):

    split_before = "<script>window.__preloadedData = "
    split_after = "</script>"

    @classmethod
    def article_text(cls, url: str) -> str:
        if "nytimes.com/live/" in url:
            return None
        html_str: str = requests.get(url).text
        json_str: str = html_str.split(cls.split_before)[1].split(cls.split_after)[0]
        ...


class GRDScraper(Scraper):

    split_before = """<div class="article-body-commercial-selector article-body-viewer-selector  dcr-1g5o3j6">"""
    split_after = '<gu-island name="SlotBodyEnd" priority="feature" deferUntil="visible"'
    split_before_2 = """<a data-ignore="global-link-styling" href="#EmailSignup-skip-link-11" class="dcr-1r8wkpb">"""
    split_after_2 = "</figure>"

    @classmethod
    def article_text(cls, url: str) -> str:
        html_str: str = requests.get(url).text
        article_html_str: str = html_str.split(cls.split_before)[1].split(cls.split_after)[0]
        article_html_str = article_html_str.split(cls.split_before_2)[0]
        if len(article_html_str.split(cls.split_before_2)) > 1:
            article_html_str += " " + article_html_str.split(cls.split_after_2)[1]
        article_str = BeautifulSoup(article_html_str).text
        return article_str
    

class CBSScraper(Scraper):

    split_before = """<script type="application/ld+json">"""
    split_after = "</script>"

    @classmethod
    def article_text(cls, url: str) -> str:
        if 'cbsnews.com/video/' in url:
            return None
        html_str: str = requests.get(url).text
        json_str: str = html_str.split(cls.split_before)[1].split(cls.split_after)[0]
        json_data: dict = json.loads(json_str)
        article_text: str = unicodedata.normalize('NFKC', json_data['articleBody'])
        return article_text
    

class WSJScraper(Scraper):


    @classmethod
    def article_text(cls, url:str) -> str:
        html_str: str = requests.get(url).text
        ...

class ABCUSScraper(Scraper):

    @classmethod
    def article_text(cls, url: str) -> str:
        html_str: str = requests.get(url).text
        json_str: str = html_str.split(";window['__abcnews__']=")[1].split(';</script>')[0]
        json_obj: dict = json.loads(json_str)
        article_json: dict = json_obj['page']['content']['story']['data']['mainComponents']
        article_json = [obj['props']['body'] for obj in article_json if obj['name'] == 'Body'][0]
        assert len(article_json) == 1
        article_json = [i['content'] for i in article_json[0] if i['type'] == 'p'][:-1]
        article = ""
        for para in article_json:
            for bit in para:
                if isinstance(bit, str):
                    article += bit + " "
                elif isinstance(bit, dict):
                    for bjt in bit['content']:
                        if isinstance(bjt, str):
                            article += bjt + " "
                        else:
                            raise ValueError()
                else:
                    raise ValueError()
        return article

scrapers: Dict[str, Scraper] = {
    "NYT World": NYTScraper,
    "BBC World": BBCScraper,
    "SBS World": SBSScraper,
    "SBS Aus": SBSScraper,
    "SMH World": SMHScraper,
    "CNN World": CNNScraper,
    "GRD World": GRDScraper,
    "CBS World": CBSScraper,
    "WSJ World": WSJScraper,
    "ABCUS Top": ABCUSScraper,
}


def pull_articles(config: dict):
    db = DBHandler(config['local'])
    articles = []
    feeds = RSSFeeds.pull(config['rss'])
    for feed in feeds:
        scraper: Scraper = scrapers[feed.name]
        for entry in feed.entries:
            found_article = db.run_sql("""
                select id from articles where url = %(url)s
            """, {"url": entry.article_url})
            if found_article:
                print('Already pulled: ', entry.article_url)
                continue
            
            article_text = scraper.article_text(entry.article_url)
            if not article_text:
                print('No article: ', entry.article_url)
            else:
                db.insert_row("articles", {
                    "feed": feed.name,
                    "ts": entry.timestamp,
                    "title": entry.title,
                    "subtitle": entry.summary,
                    "url": entry.article_url,
                    "article": article_text
                })
                print('Pulled: ', feed.name, entry.title)
    return articles

if __name__ == "__main__":
    config = json.load(open("./config.json"))
    pull_articles(config)