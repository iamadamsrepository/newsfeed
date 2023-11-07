from dataclasses import dataclass
import datetime as dt
from time import mktime
from typing import List
import feedparser

@dataclass
class RSSEntry:
    feed: str
    # TODO tags: List[str]
    title: str
    summary: str
    article_url: str
    # TODO image_url: str
    timestamp: dt.datetime


class RSSFeeds:
    def __init__(self, urls: List[str], max_entries_per_feed=8) -> None:
        self.urls  = urls
        self.max_entries_per_feed = max_entries_per_feed

        self.feeds = [feedparser.parse(url) for url in urls]
        self.parse_entries()

    def parse_entries(self):
        self.entries = []
        for feed in self.feeds:
            feed_title = feed['feed']['title']
            for entry in feed['entries'][:self.max_entries_per_feed]:
                if entry['title_detail']['type'] != 'text/plain':
                    raise ValueError()
                title = entry['title']
                if entry['summary_detail']['type'] != 'text/html':
                    raise ValueError()
                summary = entry['summary']
                article_url = entry['link']
                timestamp = dt.datetime.fromtimestamp(mktime(entry['published_parsed']))
                self.entries.append(RSSEntry(feed_title, title, summary, article_url, timestamp))
       

urls = [
    "http://feeds.bbci.co.uk/news/world/rss.xml",
    "https://www.smh.com.au/rss/world.xml",
    "https://www.aljazeera.com/xml/rss/all.xml",
    "https://feeds.skynews.com/feeds/rss/world.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"
]