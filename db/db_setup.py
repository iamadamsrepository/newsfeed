import json

from db_connection import DBHandler


def main():
    config = json.load(open("./db/config.json"))["local"]
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
    create_article_embeddings_table = """
        create table if not exists article_embeddings (
            article_id int not null,
            embedding text not null,
            constraint fk_article_id foreign key (article_id) references articles(id),
            primary key (article_id)
        )
    """
    # create_article_summaries_table = """
    #     create table if not exists article_summaries (
    #         article_id int not null,
    #         summary text not null,
    #         constraint fk_article_id foreign key (article_id) references articles(id),
    #         primary key (article_id)
    #     )
    # """
    create_stories_table = """
        create table if not exists stories (
            id serial primary key,
            ts timestamp not null,
            title text not null,
            summary text not null,
            digest_id int,
            digest_description text
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
    create_keywords_table = """
        create table if not exists keywords (
            id serial primary key,
            keyword text not null
        )
    """
    create_story_keywords_table = """
        create table if not exists story_keywords (
            story_id int not null,
            keyword_id int not null,
            constraint fk_story_id foreign key (story_id) references stories(id) on delete cascade,
            constraint fk_keyword_id foreign key (keyword_id) references keywords(id) on delete cascade,
            primary key (story_id, keyword_id)
        )
    """
    db.run_sql_no_return(create_providers_table)
    db.run_sql_no_return(create_articles_table)
    db.run_sql_no_return(create_article_embeddings_table)
    # db.run_sql_no_return(create_article_summaries_table)
    db.run_sql_no_return(create_stories_table)
    db.run_sql_no_return(create_story_articles_table)
    db.run_sql_no_return(create_keywords_table)
    db.run_sql_no_return(create_story_keywords_table)
    # providers = pd.read_csv('./db/providers.csv')
    # for _, row in providers.iterrows():
    #     db.insert_row("providers", dict(row))
    ...


if __name__ == "__main__":
    main()
