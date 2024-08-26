import json
from db_connection import DBHandler
import pandas as pd

def main():
    config = json.load(open("./db/config.json"))["aws"]
    db = DBHandler(config)
    create_articles_table = """
        create table if not exists articles (
            id serial primary key,
            ts timestamp,
            provider_id int not null,
            title text not null,
            subtitle text not null,
            url text not null,
            body text not null,
            constraint fk_provider_id foreign key (provider_id) references providers(id)
        )
    """
    create_embeddings_table = """
        create table if not exists embeddings (
            article_id int not null,
            embedding text not null,
            constraint fk_article_id foreign key (article_id) references articles(id),
            primary key (article_id)
        )
    """
    create_article_summaries_table = """
        create table if not exists article_summaries (
            article_id int not null,
            summary text not null,
            constraint fk_article_id foreign key (article_id) references articles(id),
            primary key (article_id)
        )
    """
    create_stories_table = """
        create table if not exists stories (
            id serial primary key,
            ts timestamp not null,
            title text not null,
            summary text not null
        )
    """
    create_story_articles_table = """
        create table if not exists story_articles (
            story_id int not null,
            article_id int not null,
            constraint fk_story_id foreign key (story_id) references stories(id),
            constraint fk_article_id foreign key (article_id) references articles(id)
        )
    """
    create_providers_table = """
        create table if not exists providers (
            id serial not null primary key,
            name text not null,
            url text not null,
            favicon_url text not null
        )
    """
    db.run_sql_no_return(create_providers_table)
    db.run_sql_no_return(create_articles_table)
    db.run_sql_no_return(create_embeddings_table)
    db.run_sql_no_return(create_article_summaries_table)
    db.run_sql_no_return(create_stories_table)
    db.run_sql_no_return(create_story_articles_table)
    providers = pd.read_csv('./db/providers.csv')
    for _, row in providers.iterrows():
        db.insert_row("providers", dict(row))
    ...


if __name__ == "__main__":
    main()
