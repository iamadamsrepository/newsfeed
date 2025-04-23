import argparse
import json

from openai import OpenAI

from db.db_connection import DBHandler
from db.db_objects import ArticleRow, StoryRow
from digest_status import DigestStatus, digest_status_transition


def get_embedding(text, client: OpenAI, model="text-embedding-3-large"):
    return client.embeddings.create(input=[text], model=model).data[0].embedding


def get_article_embedding(article: ArticleRow, client: OpenAI):
    return get_embedding(article.title + "\n" + article.subtitle + "\n" + " ".join(article.body.split()[:800]), client)


def get_story_embedding(story: StoryRow, client: OpenAI):
    return get_embedding(story.ts.date().isoformat() + "\t" + story.title + "\n" + story.summary, client)


@digest_status_transition(
    expected_status=DigestStatus.ARTICLES_COLLECTED,
    final_status=DigestStatus.ARTICLES_EMBEDDED,
)
def embed_articles(db_config: dict, client: OpenAI):
    db = DBHandler(db_config)
    sql_out = db.run_sql(
        """
        select a.*
        from articles a
        left outer join article_embeddings e
        on a.id = e.article_id
        where e.article_id is null
    """
    )
    unembedded_articles = [ArticleRow(*a) for a in sql_out]
    embedded = 0
    print(f"Embedding {len(unembedded_articles)} articles")
    for article in unembedded_articles:
        embedding = get_article_embedding(article, client)
        embedded += 1
        print(f"{embedded=}", end="\r")
        db.insert_row("article_embeddings", {"article_id": article.id, "embedding": str(embedding)})


@digest_status_transition(
    expected_status=DigestStatus.STORIES_GENERATED,
    final_status=DigestStatus.STORIES_EMBEDDED,
)
def embed_stories(db_config: dict, client: OpenAI):
    db = DBHandler(db_config)
    sql_out = db.run_sql(
        """
        select s.*
        from stories s
        left outer join story_embeddings e
        on s.id = e.story_id
        where e.story_id is null
    """
    )
    unembedded_stories = [StoryRow(*s) for s in sql_out]
    embedded = 0
    print(f"Embedding {len(unembedded_stories)} stories")
    for story in unembedded_stories:
        embedding = get_story_embedding(story, client)
        embedded += 1
        print(f"{embedded=}", end="\r")
        db.insert_row("story_embeddings", {"story_id": story.id, "embedding": str(embedding)})


if __name__ == "__main__":
    client = OpenAI(api_key=json.load(open("./config.json"))["openai_api_key"])
    config = json.load(open("./config.json"))["railway"]
    parser = argparse.ArgumentParser()
    modes = ["articles", "stories"]
    parser.add_argument("--mode", choices=modes, help="Choose whether to embed articles or stories.")
    args = parser.parse_args()
    mode = getattr(args, "mode", None)
    if mode is None or mode not in modes:
        parser.print_help()
        exit(1)

    if mode == "articles":
        embed_articles(config, client)
    elif mode == "stories":
        embed_stories(config, client)
