import json
from db_connection import DBHandler
import pandas as pd

def main():
    config = json.load(open("./db/config.json"))["db"]
    db = DBHandler(config)
    create_articles_table = """
        create table if not exists articles (
            id serial primary key,
            ts timestamp,
            feed text not null,
            title text not null,
            subtitle text not null,
            url text not null,
            article text not null
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
    create_clusters_table = """
        create table if not exists clusters (
            id serial primary key,
            ts timestamp not null,
            title text not null,
            summary text not null
        )
    """
    create_cluster_articles_table = """
        create table if not exists cluster_articles (
            cluster_id int not null,
            article_id int not null,
            constraint fk_cluster_id foreign key (cluster_id) references clusters(id),
            constraint fk_article_id foreign key (article_id) references articles(id)
        )
    """
    create_providers_table = """
        create table if not exists providers (
            id serial not null primary key,
            name text not null,
            url text not null,
            favicon_url text not null,
            scrape boolean not null default false,
            scraper text
        )
    """
    create_feeds_table = """
        create table if not exists feeds (
            name text not null,
            provider_id int not null,
            url text not null,
            category text not null,
            constraint fk_provider_id foreign key (provider_id) references providers(id)
        )
    """
    db.run_sql_no_return(create_articles_table)
    db.run_sql_no_return(create_embeddings_table)
    db.run_sql_no_return(create_article_summaries_table)
    db.run_sql_no_return(create_clusters_table)
    db.run_sql_no_return(create_cluster_articles_table)
    db.run_sql_no_return(create_providers_table)
    db.run_sql_no_return(create_feeds_table)
    # providers = pd.read_csv('./db/providers.csv')
    # for _, row in providers.iterrows():
    #     db.insert_row("providers", dict(row))
    # feeds = pd.read_csv('./db/feeds.csv')
    # for _, row in feeds.iterrows():
    #     db.insert_row("feeds", dict(row))
    ...


if __name__ == "__main__":
    main()
