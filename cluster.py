import datetime as dt
import json
import re
from collections import namedtuple
from typing import List, Tuple

import numpy as np
from hdbscan import HDBSCAN
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from openai import OpenAI
from openai.types.chat.chat_completion import ChatCompletion

from db.db_connection import DBHandler

ArticleInfo = namedtuple("ArticleInfo", ["id", "url", "ts", "title", "subtitle", "body", "provider", "embedding"])


def get_story_headline_and_summary(story: List[ArticleInfo], client: OpenAI, retries=0) -> Tuple[str, str, List[str]]:
    response_format = {
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
                        "description": "A list of named entities including names, places, events and institutions related to the article.",
                        "items": {"type": "string"},
                    },
                },
                "required": ["story_summary", "coverage_summary", "headline", "keywords"],
                "additionalProperties": False,
            },
        },
    }
    messages = [
        {
            "role": "system",
            "content": "You take in headlines and article text from a collection of articles about a news story. "
            "You need to provide a headline, story summary, coverage summary and keywords for the story. "
            "The headline should be up to 15 words, the story summary up to 150 words, the coverage summary up to 100 words, and up to 6 keywords. "
            "The headline should be a brief, attention-grabbing title for the story."
            "The story summary should be a concise overview of the story, including the most important information. "
            "The coverage summary should compare and contrast the way the story is told between the articles. "
            "The keywords should be names, places, events and institutions related to the story.",
        },
        {
            "role": "user",
            "content": "Here are the headlines and summaries of the articles about the story:\n\n"
            + "\n\n".join(
                [
                    f"{a.provider}\t{a.ts.strftime('%Y-%m-%d')}\n{a.title}\n{a.subtitle}\n{' '.join(a.body.split()[:200])}"
                    for a in story
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
            raise ValueError
        return get_story_headline_and_summary(story, client, retries + 1)
    return content["headline"], content["story_summary"], content["coverage_summary"], content["keywords"]


def get_article_embeddings(db: DBHandler) -> list[ArticleInfo]:
    sql_out = db.run_sql(
        f"""
        select a.id, a.url, a.ts, a.title, a.subtitle, a.body, 
        p.name, e.embedding
        from articles a
        left join article_embeddings e 
        on a.id = e.article_id
        left join providers p
        on a.provider_id = p.id
        where a.ts > '{(dt.datetime.now() - dt.timedelta(hours=72)).strftime('%Y-%m-%d %H:%M:%S')}'
        and e.embedding is not null
    """
    )
    return [ArticleInfo(a[0], a[1], a[2], a[3], a[4], a[5], a[6], eval(a[7])) for a in sql_out]


def cluster_into_stories(articles: List[ArticleInfo]) -> List[List[ArticleInfo]]:
    clusterer = HDBSCAN(min_cluster_size=3, metric="euclidean", cluster_selection_method="eom")
    labels = clusterer.fit_predict([a.embedding for a in articles])
    stories: list[list[ArticleInfo]] = []
    for i in range(len(np.unique(labels))):
        cluster_articles = [a for a, label in zip(articles, labels) if label == i]
        n_providers = len(set(a.provider for a in cluster_articles))
        if n_providers >= 3 and len(cluster_articles) >= 3:
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
    articles: List[ArticleInfo],
    headline: str,
    summary: str,
    coverage: str,
    keywords: List[str],
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
    for keyword in keywords:
        keyword_id = db.run_sql("select id from keywords where keyword = %s", (keyword,))
        if keyword_id:
            keyword_id = keyword_id[0][0]
        else:
            db.insert_row("keywords", {"keyword": keyword})
            keyword_id = db.run_sql("select max(id) from keywords")[0][0]
        db.insert_row("story_keywords", {"story_id": story_id, "keyword_id": keyword_id})


def print_story(articles: List[ArticleInfo], headline: str, summary: str, coverage: str, keywords: List[str]):
    n_providers = len(set(a.provider for a in articles))
    print("====================================")
    print(
        f"Wrote story '{headline}' from {len(articles)} articles and {n_providers} providers:\n{keywords=}\n{summary=}\n{coverage=}"
    )
    for a in articles:
        print("\t" + a.provider + "\t" + a.title + "\n\t\t" + a.url)


def cluster_articles(db_config: dict, client: OpenAI, dry_run=False):
    db = DBHandler(db_config)
    articles = get_article_embeddings(db)
    stories = cluster_into_stories(articles)

    digest_id = (db.run_sql("select coalesce(max(digest_id), 0) from stories")[0][0] or -1) + 1
    digest_description = dt.date.today().strftime(f"%Y%m%d-{digest_id}")
    for articles in stories:
        headline, story_summary, coverage_summary, keywords = get_story_headline_and_summary(articles, client)
        keywords = [sk for k in keywords if (sk := sanitize_keyword(k))]
        write_story_to_db(
            db, articles, headline, story_summary, coverage_summary, keywords, digest_id, digest_description
        )
        print_story(articles, headline, story_summary, coverage_summary, keywords)
        ...


if __name__ == "__main__":
    config = json.load(open("./config.json"))
    client = OpenAI(api_key=config["openai_api_key"])
    cluster_articles(config["local"], client, dry_run=False)
