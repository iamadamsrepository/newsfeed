from typing import Dict, Set

from newspaper.article import Article


def is_blacklisted(article: Article, blacklist_categories: Set[str]) -> bool:
    for category in blacklist_categories:
        if f"/{category}/" in article.url or f"/{category}." in article.url or f".{category}." in article.url:
            return True
    return False


def is_whitelisted(article: Article, whitelist_categories: Set[str]) -> bool:
    for category in whitelist_categories:
        if f"/{category}/" in article.url or f"/{category}." in article.url or f".{category}." in article.url:
            return True
    return False


def check_article(provider_name: str, article: Article) -> bool:
    criteria = provider_criteria[provider_name]
    if whitelist := criteria.get("whitelist_categories"):
        if not is_whitelisted(article, whitelist):
            return False
    if blacklist := criteria.get("blacklist_categories"):
        if is_blacklisted(article, blacklist):
            return False
    return True


provider_criteria: Dict[str, Dict[str, Set[str]]] = {
    "9 News": {"whitelist_categories": {"national", "world"}},
    "ABC News": {"blacklist_categories": {"everyday"}},
    "Al Jazeera": {"blacklist_categories": {"balkans", "liveblog", "sports"}},
    "BBC News": {"blacklist_categories": {"culture", "live", "reel", "travel", "videos"}},
    "CBC News": {"whitelist_categories": {"news"}},
    "CNN": {
        "blacklist_categories": {
            "cars",
            "entertainment",
            "sport",
            "style",
            "travel",
            "date",
            "audio",
            "mundo",
            "video",
            "food",
            "health",
            "ciencia",
            "latinoamerica",
            "weather",
        },
        "whitelist_categories": {"cnn"},
    },
    "DW": {"blacklist_categories": set()},
    "EuroNews": {"blacklist_categories": {"culture", "green", "tag", "travel", "video"}},
    "Financial Review": {"blacklist_categories": {"life-and-luxury", "topic"}},
    "Forbes": {"blacklist_categories": {"video", "forbesvideo", "forbes-research"}, "whitelist_categories": {"sites"}},
    "France24": {
        "blacklist_categories": {"archives", "live-news", "sponsored-content", "sport", "tv-shows", "video"},
        "whitelist_categories": set(),
    },
    "Fox News": {
        "blacklist_categories": {
            "radio",
            "video",
            "category",
            "deals",
            "media",
            "entertainment",
            "food-drink",
            "health",
            "lifestyle",
            "opinion",
            "sports",
            "story",
            "travel",
            "weather-news",
            "iheart",
            "outkick",
        }
    },
    "Hindustan Times": {
        "whitelist_categories": {"world-news"},
    },
    "MSNBC": {"blacklist_categories": set()},
    "news.com.au": {"whitelist_categories": {"breaking-news", "finance", "national", "technology", "world"}},
    "News 18": {"whitelist_categories": {"business", "elections", "india", "politics", "tech", "world"}},
    "NPR": {"blacklist_categories": {"podcasts", "sections", "series", "transcripts"}},
    "SBS News": {"blacklist_categories": {"audio", "food", "sport", "whats-on", "language"}},
    "Sky News Australia": {
        "blacklist_categories": {"stream", "listen", "podcast-episode", "video"},
        "whitelist_categories": {"skynews"},
    },
    "The Age": {"blacklist_categories": {"culture", "goodfood", "living", "property", "sport"}},
    "The Associated Press": {"whitelist_categories": {"article"}},
    "The Canberra Times": {"whitelist_categories": {"story"}},
    "The Economist": {"blacklist_categories": set()},
    "The Globe and Mail": {
        "blacklist_categories": {"arts", "drive", "life", "podcast", "real-estate", "sports", "standards-editor"}
    },
    "The Guardian": {
        "blacklist_categories": {
            "audio",
            "books",
            "commentisfree",
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
    "The Independent": {"whiteliest_categories": {"news"}},
    "The New York Times": {
        "blacklist_categories": {
            "arts",
            "athletic",
            "cooking",
            "crosswords",
            "espanol",
            "interactive",
            "pageoneplus",
            "podcasts",
            "recipes",
            "reviews",
            "nyregion",
            "movies",
            "section",
            "live",
            "athletic",
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
    # "The Times of India": {}
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
            "weather",
            "wellness",
        }
    },
    "Yahoo News": {"whitelist_categories": {"news"}},
}
