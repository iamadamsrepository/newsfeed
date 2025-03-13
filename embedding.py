import json

from openai import OpenAI

from db.db_connection import DBHandler
from db.db_objects import ArticleRow, StoryRow


def get_embedding(text, client: OpenAI, model="text-embedding-3-large"):
    return client.embeddings.create(input=[text], model=model).data[0].embedding


def get_article_embedding(article: ArticleRow, client: OpenAI):
    return get_embedding(article.title + "\n" + article.subtitle + "\n" + " ".join(article.body.split()[:800]), client)


def get_story_embedding(story: StoryRow, client: OpenAI):
    return get_embedding(story.ts.date().isoformat() + "\t" + story.title + "\n" + story.summary, client)


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
    config = json.load(open("./config.json"))["pi"]
    embed_articles(config, client)
    embed_stories(config, client)
