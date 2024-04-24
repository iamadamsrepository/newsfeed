import json
from db_connection import DBHandler


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
    db.run_sql_no_return(create_articles_table)
    db.run_sql_no_return(create_embeddings_table)
    db.run_sql_no_return(create_article_summaries_table)
    db.run_sql_no_return(create_clusters_table)
    db.run_sql_no_return(create_cluster_articles_table)


if __name__ == "__main__":
    main()
