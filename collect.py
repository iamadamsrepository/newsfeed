import datetime as dt
import io
import json
import re
import threading
import time
from typing import List
from zoneinfo import ZoneInfo

import numpy as np
import requests
from newspaper import Config, Source
from newspaper.article import Article, ArticleDownloadState
from PIL import Image

from db.db_connection import DBHandler
from db.db_objects import ProviderRow
from provider_criteria import check_article

# as DB table? "Australia", "Australia/Sydney", "AEDT"
TIMEZONES = {
    "Australia": "Australia/Sydney",
    "UK": "Europe/London",
    "USA": "America/New_York",
    "Canada": "America/Toronto",
    "France": "Europe/Paris",
    "Europe": "Europe/Paris",
    "India": "Asia/Kolkata",
    "Qatar": "Asia/Qatar",
    "The Associated Press": "Australia/Sydney",
}
TIMEZONES: dict[str, ZoneInfo] = {k: ZoneInfo(v) for k, v in TIMEZONES.items()}


def is_logo_by_colors(image: Image, color_threshold=10):
    colors = np.unique(np.array(image.convert("RGB")).reshape(-1, 3), axis=0)
    return len(colors) < color_threshold  # If very few colors, likely a logo


def has_transparency(image: Image):
    if image.mode == "RGBA":
        return image.getchannel("A").getextrema()[0] < 255  # Alpha channel check
    return False


def should_keep_image(url: str):
    try:
        response = requests.get(url, allow_redirects=True, timeout=5)
        content_type = response.headers.get("Content-Type", "")
        if not content_type.startswith("image/"):
            return False
        image = Image.open(io.BytesIO(response.content))
        if image.size[0] < 100 or image.size[1] < 100:
            return False
        if has_transparency(image):
            return False
        if is_logo_by_colors(image):
            return False
        return True
    except requests.RequestException:
        return False


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
        self.config.disable_category_cache = True
        self.config.memorize_articles = False
        self.articles = []

    def collect(self):
        self.sources: dict[str, Source] = {}

        def build_source(provider: ProviderRow):
            s = Source(provider.url, config=self.config)
            s.clean_memo_cache()
            s.build(only_homepage=True)
            self.sources[provider.name] = s

        threads: list[threading.Thread] = [threading.Thread(target=build_source, args=(p,)) for p in self.providers]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        def download_articles(provider: ProviderRow):
            source = self.sources[provider.name]
            for article in source.articles:
                if self.article_acceptance_criterion(provider, article):
                    # print(f"Accepted: {article.title}, {article.url}")
                    timezone = TIMEZONES.get(provider.name, TIMEZONES[provider.country])
                    date = article.publish_date.date()
                    if article.publish_date.time() == dt.time(0, 0):
                        ts = article.publish_date.replace(hour=12, tzinfo=timezone).astimezone(ZoneInfo("UTC"))
                    else:
                        ts = article.publish_date.replace(tzinfo=timezone).astimezone(ZoneInfo("UTC"))
                    self.articles.append(
                        {
                            "provider_id": provider.id,
                            "date": date,
                            "ts": ts,
                            "title": article.title,
                            "url": article.url.split("?")[0],
                            "body": re.sub(r"\s+", " ", article.text),
                            "subtitle": article.meta_description,
                            "image_url": article.top_image,
                            "image_urls": json.dumps([i for i in article.images if should_keep_image(i)]),
                        }
                    )

        threads = []
        for provider in self.providers:
            source = self.sources[provider.name]
            print(f"{provider.name},\t{len(source.articles)} articles\t{provider.url}")
            thread = threading.Thread(target=download_articles, args=(provider,))
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()

    def article_acceptance_criterion(self, provider: ProviderRow, article: Article) -> bool:
        print(article.url)
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
        try:
            article.parse()
        except Exception:
            time.sleep(2)
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
    db = DBHandler(config["pi"])
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
    print(f"\n\nCollected {len(collector.articles)} Articles")
    for provider in collector.providers:
        provider_articles = [article for article in collector.articles if article["provider_id"] == provider.id]
        print(f"{provider.name}: {len(provider_articles)} articles")

    if not dry_run:
        written_count = 0
        provider_article_count = {provider.name: 0 for provider in collector.providers}
        for article in collector.articles:
            found_article = db.run_sql(
                """
            select id from articles where url = %(url)s
            """,
                {"url": article["url"]},
            )[0][0]
            if found_article:
                continue
            db.insert_row("articles", article)
            written_count += 1
            provider_article_count[next(p.name for p in collector.providers if p.id == article["provider_id"])] += 1

        print(f"\n\nWrote {written_count} articles")
        for provider, count in provider_article_count.items():
            print(f"{provider}: {count} articles")


if __name__ == "__main__":
    config = json.load(open("./config.json"))
    run_collector(config, dry_run=False)
