from typing import Dict, Set

from newspaper.article import Article


def is_blacklisted(article: Article, blacklist_categories: Set[str]) -> bool:
    for category in blacklist_categories:
        if f"/{category}/" in article.url or f"/{category}." in article.url:
            return True
    return False


def check_article(provider_name: str, article: Article) -> bool:
    criteria = provider_criteria[provider_name]
    blacklist_categories = criteria.get("blacklist_categories", set())
    return not is_blacklisted(article, blacklist_categories)


provider_criteria: Dict[str, Dict[str, Set[str]]] = {
    "ABC": {"blacklist_categories": {"everyday"}},
    "Al Jazeera": {"blacklist_categories": {"balkans", "liveblog", "sports"}},
    "BBC": {"blacklist_categories": {"culture", "live", "reel", "travel", "videos"}},
    "CNN": {"blacklist_categories": {"cars", "entertainment", "sport", "style", "travel"}},
    "DW": {"blacklist_categories": set()},
    "Euronews": {"blacklist_categories": {"culture", "travel"}},
    "Financial Review": {"blacklist_categories": {"life-and-luxury", "topic"}},
    "Fox News": {
        "blacklist_categories": {"entertainment", "lifestyle", "media", "personal-finance", "sports", "travel"}
    },
    "Hindustan Times": {"blacklist_categories": {"cricket", "entertainment", "lifestyle", "trending"}},
    "MSNBC": {"blacklist_categories": set()},
    "NPR": {"blacklist_categories": {"podcasts", "sections", "series", "transcripts"}},
    "SBS": {"blacklist_categories": {"audio", "food", "sport", "whats-on", "language"}},
    "Sky News Australia": {"blacklist_categories": set()},
    "The Age": {"blacklist_categories": {"culture", "goodfood", "living", "property", "sport"}},
    "The Associated Press": {"blacklist_categories": set()},
    "The Economist": {"blacklist_categories": set()},
    "The Globe and Mail": {
        "blacklist_categories": {"arts", "drive", "life", "podcast", "real-estate", "sports", "standards-editor"}
    },
    "The Guardian": {
        "blacklist_categories": {
            "audio",
            "culture",
            "film",
            "food",
            "football",
            "gnm-press-office",
            "help",
            "lifeandstyle",
            "music",
            "society",
            "sport",
            "tv-and-radio",
            "video",
        }
    },
    "The New York Times": {
        "blacklist_categories": {
            "arts",
            "athletic",
            "crosswords",
            "espanol",
            "interactive",
            "pageoneplus",
            "podcasts",
            "reviews",
        }
    },
    "The Sydney Morning Herald": {
        "blacklist_categories": {
            "culture",
            "fashion",
            "goodfood",
            "lifestyle",
            "live-blog",
            "living",
            "property",
            "sport",
            "topic",
            "traveller",
        }
    },
    "The Telegraph": {
        "blacklist_categories": {
            "cricket",
            "football",
            "golf",
            "health-fitness",
            "royal-family",
            "rugby-union",
            "snooker",
            "sport",
            "s",
            "travel",
        }
    },
    "The Washington Post": {
        "blacklist_categories": {
            "advice",
            "books",
            "entertainment",
            "food",
            "lifestyle",
            "obituaries",
            "opinions",
            "podcasts",
            "sports",
            "style",
            "travel",
            "video",
            "wellness",
        }
    },
    "9 News": {"blacklist_categories": {"motorsport", "nrl", "olympics"}},
}
