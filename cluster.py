import datetime as dt
import json
import re
from collections import Counter, namedtuple
from typing import List, Tuple

import numpy as np
from hdbscan import HDBSCAN
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from openai import OpenAI
from openai.types.chat.chat_completion import ChatCompletion

from db.db_connection import DBHandler
from digest_status import DigestStatus, digest_status_transition

ArticleInfo = namedtuple(
    "ArticleInfo", ["id", "url", "ts", "title", "subtitle", "body", "provider", "country", "embedding"]
)

STORY_TITLE_AND_SUMMARY_RESPONSE_FORMAT = {
    "type": "json_schema",
    "json_schema": {
        "name": "story_title_and_summary",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "story_summary": {
                    "type": "string",
                    "description": "Up to 150 words to summarise the story based on the articles.",
                },
                "coverage_summary": {
                    "type": "string",
                    "description": "Up to 100 words to describe the ways the different articles told the story.",
                },
                "headline": {
                    "type": "string",
                    "description": "Up to 15 words to headline the story based on the articles.",
                },
                "keywords": {
                    "type": "array",
                    "description": "A list of up to 10 named entities relating to the story, such as names, places, events or institutions.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "keyword": {"type": "string", "description": "keyword"},
                            "type": {
                                "type": "string",
                                "enum": ["PERSON", "PLACE", "EVENT", "INSTITUTION", "CONCEPT", "OTHER"],
                            },
                        },
                        "required": ["keyword", "type"],
                        "additionalProperties": False,
                    },
                },
            },
            "required": ["story_summary", "coverage_summary", "headline", "keywords"],
            "additionalProperties": False,
        },
    },
}

STORY_TITLE_AND_SUMMARY_SYSTEM_MESSAGE = {
    "role": "system",
    "content": "You take in headlines and article text from a collection of articles about a news story. "
    "You need to provide a headline, story summary, coverage summary and keywords for the story. "
    "The headline should be up to 15 words, the story summary up to 150 words, the coverage summary up to 100 words, and up to 10 keywords. "
    "The headline should be a brief, attention-grabbing title for the story."
    "The story summary should be a concise overview of the story. Include the most important information, and specify dates of specific events. "
    "The coverage summary should compare and contrast the way the story is told between the articles. "
    "The keywords should be names, places, events and institutions related to the story.",
}


def article_ranking_key(article: ArticleInfo):
    return article.ts


def cluster_criterion(articles: List[ArticleInfo]) -> bool:
    n_providers = len(set(a.provider for a in articles))
    n_countries = len(set(a.country for a in articles))
    return (n_providers >= 5) or (n_countries == 1 and n_providers >= 3) or (n_countries == 2 and n_providers >= 4)


def get_story_headline_and_summary(story: List[ArticleInfo], client: OpenAI, retries=0) -> Tuple[str, str, List[str]]:
    response_format = STORY_TITLE_AND_SUMMARY_RESPONSE_FORMAT
    message_articles = sorted(story, key=article_ranking_key, reverse=True)
    message_articles = message_articles[:20]  # Limit to 20 articles
    messages = [
        STORY_TITLE_AND_SUMMARY_SYSTEM_MESSAGE,
        {
            "role": "user",
            "content": "Here are the headlines and summaries of the articles about the story:\n"
            + "\n".join(
                [
                    f"{a.ts.strftime('%Y-%m-%d')}\t{a.provider} ({a.country})\n{a.title}\n{a.subtitle}\n{' '.join(a.body.split()[:200])}"
                    for a in message_articles
                ]
            ),
        },
    ]
    response: ChatCompletion = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        response_format=response_format,
        temperature=1,
        max_completion_tokens=2048,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )
    try:
        assert len(response.choices) == 1
        choice = response.choices[0]
        message = choice.message
        content = json.loads(message.content)
        assert content["story_summary"]
        assert content["coverage_summary"]
        assert content["headline"]
        assert content["keywords"]
    except (AssertionError, json.JSONDecodeError):
        print("Retrying")
        if retries == 2:
            raise
        return get_story_headline_and_summary(story, client, retries + 1)
    return content["headline"], content["story_summary"], content["coverage_summary"], content["keywords"]


def get_article_embeddings(db: DBHandler) -> list[ArticleInfo]:
    sql_out = db.run_sql(
        f"""
        select a.id, a.url, a.ts, a.title, a.subtitle, a.body,
        p.name, p.country, e.embedding
        from articles a
        left join article_embeddings e
        on a.id = e.article_id
        left join providers p
        on a.provider_id = p.id
        where a.ts > '{(dt.datetime.now() - dt.timedelta(hours=48)).strftime("%Y-%m-%d %H:%M:%S")}'
        and e.embedding is not null
    """
    )
    return [ArticleInfo(a[0], a[1], a[2], a[3], a[4], a[5], a[6], a[7], eval(a[8])) for a in sql_out]


def cluster_into_stories(articles: List[ArticleInfo]) -> List[List[ArticleInfo]]:
    clusterer = HDBSCAN(min_cluster_size=3, metric="euclidean", cluster_selection_method="eom")
    labels = clusterer.fit_predict([a.embedding for a in articles])
    stories: list[list[ArticleInfo]] = []
    for i in range(len(np.unique(labels))):
        cluster_articles = [a for a, label in zip(articles, labels) if label == i]
        if cluster_criterion(cluster_articles):
            stories.append(cluster_articles)
    return stories


def sanitize_keyword(keyword: str) -> str | None:
    keyword = keyword.lower().strip()
    keyword = re.sub(r"[^a-z0-9\s-]", "", keyword)
    keyword = " ".join(
        [WordNetLemmatizer().lemmatize(word) for word in keyword.split() if word not in set(stopwords.words("english"))]
    )  # Lemmatize & remove stopwords
    if keyword:
        return keyword
    return None


def write_story_to_db(
    db: DBHandler,
    articles: list[ArticleInfo],
    headline: str,
    summary: str,
    coverage: str,
    keywords: list[dict[str, str]],
    digest_id: int,
    digest_description: str,
):
    db.insert_row(
        "stories",
        {
            "ts": dt.datetime.now(),
            "title": headline,
            "summary": summary,
            "coverage": coverage,
            "digest_id": digest_id,
            "digest_description": digest_description,
        },
    )
    story_id = db.run_sql("select max(id) from stories")[0][0]
    for article in articles:
        db.insert_row("story_articles", {"story_id": story_id, "article_id": article.id})
    for keyword_dict in keywords:
        keyword, _type = keyword_dict["keyword"], keyword_dict["type"]
        keyword_id = db.run_sql("select id from keywords where keyword = %s and type = %s", (keyword, _type))
        if keyword_id:
            keyword_id = keyword_id[0][0]
        else:
            db.insert_row("keywords", {"keyword": keyword, "type": _type})
            keyword_id = db.run_sql("select max(id) from keywords")[0][0]
        db.insert_row("story_keywords", {"story_id": story_id, "keyword_id": keyword_id})


def print_story(articles: List[ArticleInfo], headline: str, summary: str, coverage: str, keywords: List[str]):
    n_providers = len(set(a.provider for a in articles))
    print("\n====================================\n")
    print(
        f"Wrote story '{headline}' from {len(articles)} articles and {n_providers} providers:\n{keywords=}\n{summary=}\n{coverage=}"
    )
    for a in articles:
        print("\t" + a.provider + "\t" + a.title + "\n\t\t" + a.url)


def print_stories_breakdown(stories: List[List[ArticleInfo]]):
    for i, story in enumerate(stories):
        providers = Counter([a.provider for a in story])
        print(
            f"{i}: {len(story)} articles\t{len(providers)} providers\t{list(providers.values())}\n\t{list(providers.keys())}"
        )


@digest_status_transition(
    expected_status=DigestStatus.ARTICLES_EMBEDDED,
    final_status=DigestStatus.STORIES_GENERATED,
)
def cluster_articles(db_config: dict, client: OpenAI, dry_run=False):
    db = DBHandler(db_config)
    articles = get_article_embeddings(db)
    stories = cluster_into_stories(articles)
    print_stories_breakdown(stories)

    if dry_run:
        print("Dry run, not writing to DB")
        return
    digest_id = (d if (d := db.run_sql("select max(digest_id) from stories")[0][0]) is not None else -1) + 1
    digest_description = dt.date.today().strftime(f"%Y%m%d-{digest_id}")
    for articles in stories:
        headline, story_summary, coverage_summary, keywords = get_story_headline_and_summary(articles, client)
        write_story_to_db(
            db, articles, headline, story_summary, coverage_summary, keywords, digest_id, digest_description
        )
        print_story(articles, headline, story_summary, coverage_summary, keywords)


if __name__ == "__main__":
    config = json.load(open("./config.json"))
    client = OpenAI(api_key=config["openai_api_key"])
    cluster_articles(config["railway"], client, dry_run=False)
