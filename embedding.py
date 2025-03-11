import json

from openai import OpenAI

from db.db_connection import DBHandler
from db.db_objects import ArticleRow


def get_embedding(text, client: OpenAI, model="text-embedding-3-large"):
    return client.embeddings.create(input=[text], model=model).data[0].embedding


def get_article_embedding(article: ArticleRow, client: OpenAI):
    return get_embedding(article.title + "\n" + article.subtitle + "\n" + " ".join(article.body.split()[:800]), client)


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
    for article in unembedded_articles:
        embedding = get_article_embedding(article, client)
        db.insert_row("article_embeddings", {"article_id": article.id, "embedding": str(embedding)})


if __name__ == "__main__":
    client = OpenAI(api_key=json.load(open("./config.json"))["openai_api_key"])
    config = json.load(open("./config.json"))["pi"]
    embed_articles(config, client)
