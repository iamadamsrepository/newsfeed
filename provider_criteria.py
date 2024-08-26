from typing import Callable, Dict
from newspaper.article import Article

def twp(article: Article) -> bool:
    blacklist_categories = {"food", "advice", "sports", "style", "lifestyle", "podcasts"}
    for c in blacklist_categories:
        if f"/{c}/" in article.url:
            return False
    return True

def npr(article: Article) -> bool:
    blacklist_categories = {"sections", "series", "podcasts", "transcripts"}
    for c in blacklist_categories:
        if f"/{c}/" in article.url:
            return False
    return True

def cnn(article: Article) -> bool:
    blacklist_categories = {"entertainment", "travel", "cars", "sport", "style", }
    for c in blacklist_categories:
        if f"/{c}/" in article.url:
            return False
    return True

def tec(article: Article) -> bool:
    return True

def nyt(article: Article) -> bool:
    blacklist_categories = {"arts", "podcasts", "crosswords"}
    for c in blacklist_categories:
        if f"/{c}/" in article.url:
            return False
    return True

def nbc(article: Article) -> bool:
    return True

def fox(article: Article) -> bool:
    blacklist_categories = {"media", "sports", "entertainment", "lifestyle", "personal-finance", "travel"}
    for c in blacklist_categories:
        if f"/{c}/" in article.url:
            return False
    return True

def abc(article: Article) -> bool:
    blacklist_categories = {"everyday"}
    for c in blacklist_categories:
        if f"/{c}/" in article.url:
            return False
    return True

def smh(article: Article) -> bool:
    blacklist_categories = {"property", "sport", "culture", "goodfood", "living", "topic", "traveller"}
    for c in blacklist_categories:
        if f"/{c}/" in article.url:
            return False
    if "www.domain.com.au" in article.url:
        return False
    return True

def sbs(article: Article) -> bool:
    blacklist_categories = {"audio", "whats-on", "sport", "food"}
    for c in blacklist_categories:
        if f"/{c}/" in article.url:
            return False
    return True

def n9n(article: Article) -> bool:
    blacklist_categories = {"nrl", "olympics", "motorsport"}
    for c in blacklist_categories:
        if f"/{c}/" in article.url:
            return False
    if "www.domain.com.au" in article.url:
        return False
    return True

def age(article: Article) -> bool:
    blacklist_categories = {"property", "goodfood", "culture", "sport", "living"}
    for c in blacklist_categories:
        if f"/{c}/" in article.url:
            return False
    if "www.drive.com.au" in article.url:
        return False
    return True

def gda(article: Article) -> bool:
    blacklist_categories = {"film", "books", "lifeandstyle", "tv-and-radio", "sport", "society", "football"}
    for c in blacklist_categories:
        if f"/{c}/" in article.url:
            return False
    return True

def afr(article: Article) -> bool:
    blacklist_categories = {"life-and-luxury", "topic"}
    for c in blacklist_categories:
        if f"/{c}/" in article.url:
            return False
    return True

def eur(article: Article) -> bool:
    blacklist_categories = {"culture", "travel"}
    for c in blacklist_categories:
        if f"/{c}/" in article.url:
            return False
    return True

def hin(article: Article) -> bool:
    blacklist_categories = {"lifestyle", "trending", "entertainment", "cricket"}
    for c in blacklist_categories:
        if f"/{c}/" in article.url:
            return False
    return True

def dw(article: Article) -> bool:
    return True

def tgm(article: Article) -> bool:
    blacklist_categories = {"podcast", "arts", "sports", "drive", "standards-editor", "life", "real-estate"}
    for c in blacklist_categories:
        if f"/{c}/" in article.url:
            return False
    return True

def tlg(article: Article) -> bool:
    if len(article.url) < 50:
        return False
    blacklist_categories = {"travel", "health-fitness", "golf", "rugby-union", "s", "football", "snooker", "sport", "royal-family", "cricket"}
    for c in blacklist_categories:
        if f"/{c}/" in article.url:
            return False
    return True

def alj(article: Article) -> bool:
    return True

def tap(article: Article) -> bool:
    return True

def bbc(article: Article) -> bool:
    return True

def sna(article: Article) -> bool:
    return True

provider_criteria: Dict[str, Callable[[Article], bool]] = {
    "The Washington Post": twp,
    "NPR": npr,
    "CNN": cnn,
    "The Associated Press": tap,
    "The Economist": tec,
    "The New York Times": nyt,
    "MSNBC": nbc,
    "Fox News": fox,
    "ABC": abc,
    "The Sydney Morning Herald": smh,
    "SBS": sbs,
    "9 News": n9n,
    "The Age": age,
    "The Guardian Australia": gda,
    "Financial Review": afr,
    "The Guardian": gda,
    "BBC": bbc,
    "Euronews": eur,
    "Hindustan Times": hin,
    "DW": dw,
    "The Globe and Mail": tgm,
    "The Telegraph": tlg,
    "Al Jazeera": alj,
    "Sky News Australia": sna,
}