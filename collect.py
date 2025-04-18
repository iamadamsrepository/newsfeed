import datetime as dt
import io
import json
import re
import threading
import time
import warnings
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
import PIL
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
    "Japan": "Asia/Tokyo",
    "Germany": "Europe/Berlin",
}
TIMEZONES: dict[str, ZoneInfo] = {k: ZoneInfo(v) for k, v in TIMEZONES.items()}


class Collector:
    def __init__(self, db: DBHandler):
        self.db = db
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

        self.download_counter = 0
        self.write_counter = 0
        self.image_counter = 0

    def _get_providers(self) -> list[ProviderRow]:
        sql_out = self.db.run_sql(
            """
        select * from providers
    """
        )
        return [ProviderRow(*p) for p in sql_out]

    def _get_article_urls(self) -> list[str]:
        sql_out = self.db.run_sql(
            """
        select url from articles
    """
        )
        return [url for url, in sql_out]

    def _build_source(self, provider: ProviderRow, sources):
        source = Source(provider.url, config=self.config)
        source.clean_memo_cache()
        source.build(only_homepage=True)
        sources[provider.name] = source

    def _build_sources(self, providers: list[ProviderRow]) -> dict[str, Source]:
        sources = {}
        threads: list[threading.Thread] = [
            threading.Thread(target=self._build_source, args=(p, sources)) for p in providers
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        return sources

    def _format_url(self, url: str) -> str:
        url = url.split("?")[0]
        url = url.split("#")[0]
        return url

    def _format_source_article_urls(self, source: Source):
        for article in source.articles:
            article.url = self._format_url(article.url)

    def _download_source_articles(self, source: Source):
        keep_articles = []
        for article in source.articles:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                article.download()
            if article.download_state == ArticleDownloadState.FAILED_RESPONSE:
                continue
            try:
                article.parse()
            except Exception:
                time.sleep(2)
                article.parse()
            keep_articles.append(article)
            self.download_counter += 1
            print(self.download_counter, end="\r")
            time.sleep(0.1)
        source.articles = keep_articles

    def _download_articles(self, sources: dict[str, Source]):
        threads: list[threading.Thread] = [
            threading.Thread(target=self._download_source_articles, args=(s,)) for s in sources.values()
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

    def _check_downloaded_article(self, article: Article) -> bool:
        if not article.publish_date:
            return False
        if article.publish_date.date() < dt.date.today() - dt.timedelta(days=3):
            return False
        if len(article.title.split()) < 6:
            return False
        if len(article.text.split()) < 18:
            return False
        return True

    @staticmethod
    def _is_logo_by_colors(image: Image, color_threshold=100):
        colors = np.unique(np.array(image.convert("RGB")).reshape(-1, 3), axis=0)
        return len(colors) < color_threshold  # If very few colors, likely a logo

    @staticmethod
    def _has_transparency(image: Image):
        if image.mode == "RGBA":
            return image.getchannel("A").getextrema()[0] < 255  # Alpha channel check
        return False

    def _article_to_dict(self, provider: ProviderRow, article: Article) -> dict:
        timezone = TIMEZONES.get(provider.name, TIMEZONES[provider.country])
        date = article.publish_date.date()
        if article.publish_date.time() == dt.time(0, 0):
            ts = article.publish_date.replace(hour=12, tzinfo=timezone).astimezone(ZoneInfo("UTC"))
        else:
            ts = article.publish_date.replace(tzinfo=timezone).astimezone(ZoneInfo("UTC"))
        image_urls = {self._format_url(url) for url in article.images[:8]}
        # image_urls = [i for i in image_urls if self._check_image(i)]
        image_urls = []
        return {
            "provider_id": provider.id,
            "date": date,
            "ts": ts,
            "title": article.title,
            "url": article.url,
            "body": re.sub(r"\s+", " ", article.text),
            "subtitle": article.meta_description,
            "image_url": article.top_image,
            "image_urls": json.dumps(image_urls),
        }

    def _check_image(self, url: str) -> bool:
        try:
            self.image_counter += 1
            print(self.image_counter, end="\r")
            response = requests.get(url, allow_redirects=True, timeout=3)
            content_type = response.headers.get("Content-Type", "")
            if not content_type.startswith("image/"):
                return False
            image = Image.open(io.BytesIO(response.content))
            if image.size[0] < 100 or image.size[1] < 100:
                return False
            if self._has_transparency(image):
                return False
            if self._is_logo_by_colors(image):
                return False
            return True
        except (requests.RequestException, PIL.UnidentifiedImageError):
            return False

    def _format_source_articles_for_db(self, provider: ProviderRow, source: Source, formatted_articles: list[dict]):
        for article in source.articles:
            formatted_articles.append((provider.name, self._article_to_dict(provider, article)))

    def _format_articles_for_db(self, providers: list[ProviderRow], sources: dict[str, Source]) -> list[dict]:
        threads: list[threading.Thread] = []
        formatted_articles = []
        for provider_name, source in sources.items():
            provider = next(p for p in providers if p.name == provider_name)
            threads.append(
                threading.Thread(
                    target=self._format_source_articles_for_db, args=(provider, source, formatted_articles)
                )
            )
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        return formatted_articles

    def collect(self):
        print("Running Collector")
        results = {}

        providers = self._get_providers()
        print(f"Pulled {len(providers)} providers")
        article_urls = self._get_article_urls()
        print(f"Pulled {len(article_urls)} article urls")

        sources = self._build_sources(providers)
        for provider, source in sources.items():
            results[provider] = {"pulled_from_homepage": len(source.articles)}
        print(
            f"Built {len(sources)} sources, and found {sum(len(source.articles) for source in sources.values())} articles"
        )

        for provider, source in sources.items():
            self._format_source_article_urls(source)
            source.articles = [article for article in source.articles if check_article(provider, article)]
            results[provider]["accepted_articles"] = len(source.articles)
        print(f"Filtered by black/white lists, {sum(len(source.articles) for source in sources.values())} remaining")

        for provider, source in sources.items():
            source.articles = [article for article in source.articles if article.url not in article_urls]
            results[provider]["new_articles"] = len(source.articles)
        print(f"Filtered existing articles, {sum(len(source.articles) for source in sources.values())} remaining")

        print(f"Downloading {sum(len(source.articles) for source in sources.values())} articles")
        self._download_articles(sources)
        for provider, source in sources.items():
            results[provider]["downloaded_articles"] = len(source.articles)
        print(f"Downloaded {sum(len(source.articles) for source in sources.values())} articles")

        for provider, source in sources.items():
            source.articles = [article for article in source.articles if self._check_downloaded_article(article)]
            results[provider]["final"] = len(source.articles)
        print(f"Keeping {sum([len(source.articles) for source in sources.values()])} articles after article checks")

        print("Formatting for DB and checking images")
        articles = self._format_articles_for_db(providers, sources)

        print(f"Writing {len(articles)} articles to DB")
        for provider, article in articles:
            self.db.insert_row("articles", article)
            if results[provider].get("written"):
                results[provider]["written"] += 1
            else:
                results[provider]["written"] = 1
            self.write_counter += 1
            print(self.write_counter, end="\r")
        print(f"Wrote {len(articles)} articles")

        results_df = pd.DataFrame(results).T
        today = dt.date.today().isoformat()
        results_df.to_csv(f"collection_results_{today}.csv", lineterminator="\n")
        print(f"Results saved to collection_results_{today}.csv")
        print("Finished Collector")


if __name__ == "__main__":
    config = json.load(open("./config.json"))
    db = DBHandler(config["railway"])
    collector = Collector(db)
    collector.collect()
