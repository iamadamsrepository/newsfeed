import datetime as dt
from dataclasses import dataclass


@dataclass
class ProviderRow:
    id: int
    name: str
    url: str
    favicon_url: str
    country: str


@dataclass
class ArticleRow:
    id: int
    ts: dt.datetime
    provider_id: int
    title: str
    subtitle: str
    url: str
    body: str
    image_url: str
