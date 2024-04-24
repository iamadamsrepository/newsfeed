import datetime as dt
from dataclasses import dataclass


@dataclass
class ArticleRow:
    id: int
    ts: dt.datetime
    feed: str
    title: str
    subtitle: str
    url: str
    article: str