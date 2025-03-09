import datetime as dt
import json
import re
import threading
import time
from typing import List

from newspaper import Config, Source
from newspaper.article import Article, ArticleDownloadState

from db.db_connection import DBHandler
from db.db_objects import ProviderRow
from provider_criteria import check_article


class Collector:
    def __init__(self, providers: List[ProviderRow]):
        self.providers = providers
        self.config = Config()
        self.config.allow_binary_content = True  # Allow binary content
        self.config.ignored_content_types_defaults = [
            "application",
            "image",
            "video",
            "audio",
            "font",
        ]  # Set ignored content types
        self.config.requests_params["headers"][
            "User-Agent"
        ] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:135.0) Gecko/20100101 Firefox/135.0"
        self.config.memorize_articles = False
        self.articles = []

    def collect(self):
        self.sources: dict[str, Source] = {}

        def build_source(provider: ProviderRow):
            s = Source(provider.url, config=self.config)
            s.clean_memo_cache()
            s.build(
                # only_homepage=True,
                # only_in_path=True,
            )
            self.sources[provider.name] = s
            print(f"Built {provider.name}, {provider.url}: found {len(s.articles)} articles")

        threads: list[threading.Thread] = [threading.Thread(target=build_source, args=(p,)) for p in self.providers]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        def download_articles(provider: ProviderRow):
            source = self.sources[provider.name]
            for article in source.articles:
                if self.article_criterion(provider, article):
                    print(f"Accepted: {article.title}, {article.url}")
                    self.articles.append(
                        {
                            "provider_id": provider.id,
                            "ts": article.publish_date,
                            "title": article.title,
                            "url": article.url.split("?")[0],
                            "body": re.sub(r"\s+", " ", article.text),
                            "subtitle": article.meta_description,
                        }
                    )
                    ...
                else:
                    print("\t\tRejected: ", article.url)
                    ...

        threads = []
        for provider in self.providers:
            source = self.sources[provider.name]
            print(f"Provider: {provider.name}, {provider.url}. Pulling {len(source.articles)} articles")
            thread = threading.Thread(target=download_articles, args=(provider,))
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()

    def article_criterion(self, provider: ProviderRow, article: Article) -> bool:
        if not article.url:
            return False
        if "#" in article.url:
            return False
        if not check_article(provider.name, article):
            return False
        article.download()
        time.sleep(0.1)
        if article.download_state == ArticleDownloadState.FAILED_RESPONSE:
            return False
        article.parse()
        if not article.publish_date:
            return False
        if article.publish_date.date() < dt.date.today() - dt.timedelta(days=3):
            return False
        if len(article.title.split()) < 6:
            return False
        if len(article.text.split()) < 18:
            return False
        return check_article(provider.name, article)

    def print_article(self, article: Article):
        print(f"Date: {article.publish_date}")
        print(f"Title: {article.title}")
        print(f"Len: {len(article.text.split())}")
        print(f"Text: {article.text[:150]}...")
        print(f"Description: {article.meta_description}")
        print(f"Url: {article.url}")
        print("-------------------------------")


def run_collector(config: dict, dry_run=False):
    db = DBHandler(config["local"])
    providers = [
        ProviderRow(*p)
        for p in db.run_sql(
            """
        select * from providers
    """
        )
    ]
    collector = Collector(providers)
    collector.collect()
    print(f"Collected {len(collector.articles)} Articles")
    if not dry_run:
        for article in collector.articles:
            found_article = db.run_sql(
                """
                select id from articles where url = %(url)s
            """,
                {"url": article["url"]},
            )
            if found_article:
                print("Already pulled: ", article["url"])
                continue
            db.insert_row("articles", article)
        print(f"Wrote {len(collector.articles)}")


if __name__ == "__main__":
    config = json.load(open("./config.json"))
    run_collector(config, dry_run=False)
