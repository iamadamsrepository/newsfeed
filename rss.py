from dataclasses import dataclass
import datetime as dt
from time import mktime
from typing import Dict, List
import feedparser

@dataclass
class RSSEntry:
    # TODO tags: List[str]
    title: str
    summary: str
    article_url: str
    # TODO image_url: str
    timestamp: dt.datetime

@dataclass
class RSSFeed:
    name: str
    feed_title: str
    feed_url: str
    entries: List[RSSEntry]

class RSSFeeds:
    @classmethod
    def pull(cls, urls: Dict[str, str], max_entries_per_feed: int = 12) -> List[RSSFeed]:
        feeds: List[RSSFeeds] = []
        for name, url in urls.items():
            feed_data = feedparser.parse(url)
            feed = cls.parse_feed_data(name, url, feed_data, max_entries_per_feed)
            feeds.append(feed)
        return feeds

    @classmethod
    def parse_feed_data(cls, name, url: str, feed_data: dict, max_entries_per_feed: int) -> RSSFeed:
        feed_title = feed_data['feed']['title']
        entries: List[RSSEntry] = []
        for entry in feed_data['entries'][:max_entries_per_feed]:
            entries.append(cls.parse_entry(entry))
        return RSSFeed(name, feed_title, url, entries)

    @classmethod
    def parse_entry(cls, entry: dict) -> RSSEntry:
        if entry['title_detail']['type'] != 'text/plain':
            raise ValueError()
        title = entry['title']
        if 'summary_detail' not in entry:
            summary = None
        elif entry['summary_detail']['type'] != 'text/html':
            raise ValueError()
        else:
            summary = entry['summary']
        article_url = entry['link']
        entry: dict
        time_struct = entry.get('published_parsed', entry['updated_parsed'])
        timestamp = dt.datetime.fromtimestamp(mktime(time_struct))
        return RSSEntry(title, summary, article_url, timestamp)

       

all_urls = [
    # WORLD: 2AU, 3UK, 4US, 1CA, 1DE, 1QA
    "https://www.sbs.com.au/news/topic/world/feed",
    "https://www.smh.com.au/rss/world.xml",
    "http://feeds.bbci.co.uk/news/world/rss.xml",
    "https://www.theguardian.com/world/rss",
    "https://feeds.skynews.com/feeds/rss/world.xml",
    "http://rss.cnn.com/rss/edition_world.rss",
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "https://feeds.a.dj.com/rss/RSSWorldNews.xml",
    "https://feeds.washingtonpost.com/rss/world",
    "https://globalnews.ca/feed/",
    "http://rss.dw.com/rdf/rss-en-world",
    "https://www.aljazeera.com/xml/rss/all.xml",

    # AUS
    "https://www.9news.com.au/rss",
    "https://www.cyberseo.net/public-rss-feed-catalogue/Australian+News/",
    "https://www.crikey.com.au/feed/",
    "https://www.theguardian.com/australia-news/rss",
    "http://www.heraldsun.com.au/news/national/rss",
    "https://www.sbs.com.au/news/topic/australia/feed",
    "https://www.smh.com.au/rss/national.xml",
    "https://thewest.com.au/news/australia/rss",
]
