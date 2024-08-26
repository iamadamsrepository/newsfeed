import json
from openai import OpenAI

from db.db_connection import DBHandler
from db.db_objects import ArticleRow

def get_embedding(text, client: OpenAI, model="text-embedding-3-large"):
   text = text.replace("\n", " ")
   return client.embeddings.create(input=[text], model=model).data[0].embedding

def get_article_embedding(article: ArticleRow, client: OpenAI):
    return get_embedding(' '.join(article.body.split()[:600]), client)

def embed_articles(db_config: dict, client: OpenAI):
    db = DBHandler(db_config)
    sql_out = db.run_sql("""
        select a.*
        from articles a
        left outer join embeddings e 
        on a.id = e.article_id
        where e.article_id is null
    """)
    unembedded_articles = [ArticleRow(*a) for a in sql_out]
    for article in unembedded_articles:
        embedding = get_article_embedding(article, client)
        db.insert_row("embeddings", {
            "article_id": article.id,
            "embedding": str(embedding)
        })

if __name__ == "__main__":
    client = OpenAI()
    config = json.load(open("./config.json"))["db"]
    embed_articles(config, client)