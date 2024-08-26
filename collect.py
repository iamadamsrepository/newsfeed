import json
from typing import Dict, List
from newspaper.source import Source
from newspaper.article import Article
import pandas as pd
from functools import partial
from newspaper import Source
from newspaper.mthreading import fetch_news
import threading

from db.db_connection import DBHandler
from db.db_objects import ProviderRow
from provider_criteria import provider_criteria

class Collector:

    def __init__(self, providers: List[ProviderRow], config=None):
        self.providers = providers
        for p in providers:
            p.source = Source(p.url, config=config)
        self.articles = []

    def build_sources(self, clear_cache=True):
        def build_source(source: Source):
            if clear_cache:
                source.clean_memo_cache()
            source.build(only_homepage=True, only_in_path=True)

        print(f"Building {len(self.providers)} providers")
        threads = [threading.Thread(target=build_source, args=(p.source,)) for p in self.providers]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

    def pull_articles(self):
        print(f"Pulling articles")
        for p in self.providers:
            p.source.articles = p.source.articles[:20]
        fetch_news([p.source for p in self.providers], threads=16)

    def article_criterion(self, provider: ProviderRow, article: Article) -> bool:
        article.parse()
        if not article.publish_date:
            return False
        if len(article.title.split()) < 6:
            return False
        if len(article.text.split()) < 18:
            return False
        if '#' in article.url:
            return False
        return provider_criteria[provider.name](article)

    def print_article(self, article: Article):
        print(f"Date: {article.publish_date}")
        print(f"Title: {article.title}")
        print(f"Len: {len(article.text.split())}")
        print(f"Text: {article.text[:150]}...")
        print(f"Description: {article.meta_description}")
        print(f"Url: {article.url}")
        print("-------------------------------")

    def extract_information(self):
        # Extract information from each article
        for p in self.providers:
            source: Source = p.source
            provider_articles: List[Article] = list(filter(partial(self.article_criterion, p), source.articles))
            print(f"{p.name}:\tPulled {len(source.articles)} articles, {len(provider_articles)} after filter")
            ...
            self.articles += [{
                "provider_id": p.id,
                "ts": article.publish_date,
                "title": article.title,
                "url": article.url,
                "body": article.text,
                "subtitle": article.meta_description
            } for article in provider_articles]


def run_collector(config: dict, dry_run=False):
    db = DBHandler(config['db'])
    providers = [ProviderRow(*p) for p in db.run_sql("""
        select * from providers
    """)]
    collector = Collector(providers)
    collector.build_sources()
    collector.pull_articles()
    collector.extract_information()
    print(f"Collected {len(collector.articles)} Articles")
    if not dry_run:
        for article in collector.articles:
            found_article = db.run_sql("""
                select id from articles where url = %(url)s
            """, {"url": article['url']})
            if found_article:
                print('Already pulled: ', article['url'])
                continue
            db.insert_row("articles", article)
        print(f"Wrote {len(collector.articles)}")

if __name__ == "__main__":
    config = json.load(open("./config.json"))
    run_collector(config, dry_run=False)