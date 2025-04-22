import json

import pandas as pd
from db_connection import DBHandler


def main():
    config = json.load(open("./config.json"))["railway"]
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
            image_url text,
            image_urls text,
            date date,
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
    create_stories_table = """
        create table if not exists stories (
            id serial primary key,
            ts timestamp not null,
            title text not null,
            summary text not null,
            coverage text not null,
            digest_id int not null,
            digest_description text not null
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
            favicon_url text not null,
            country text not null
        )
    """
    create_keywords_table = """
        create table if not exists keywords (
            id serial primary key,
            keyword text not null,
            type text not null,
            constraint unique_keyword unique (keyword, type)
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
    create_story_embeddings_table = """ 
        create table if not exists story_embeddings (
            story_id int not null,
            embedding text not null,
            constraint fk_story_id foreign key (story_id) references stories(id),
            primary key (story_id)
        )
    """
    create_images_table = """
        create table if not exists images (
            id serial primary key,
            story_id int not null,
            url text not null,
            source_page text not null,
            height int not null,
            width int not null,
            format text not null,
            title text not null,
            constraint fk_story_id foreign key (story_id) references stories(id)
        )
    """
    create_digests_table = """
        create table if not exists digests (
            id int primary key,
            ts timestamp not null,
            status text not null
        )
    """
    create_digest_rundowns_table = """ 
        create table if not exists digest_rundowns (
            digest_id int,
            rundown_type text,
            rundown text,
            primary key (digest_id, rundown_type)
        )
    """
    create_timelines_table = """
        create table if not exists timelines (
            id serial primary key,
            digest_id int not null,
            ts timestamp,
            subject text not null,
            headline text not null,
            summary text not null,
            constraint fk_digest_id foreign key (digest_id) references digests(id),
            constraint unique_timeline unique (digest_id, subject)
        )
    """
    create_timeline_events_table = """
        create table if not exists timeline_events (
            timeline_id int not null,
            story_id int not null,
            description text not null,
            date date not null,
            date_type text not null,
            constraint fk_timeline_id foreign key (timeline_id) references timelines(id),
            constraint fk_story_id foreign key (story_id) references stories(id),
            primary key (timeline_id, description)
        )
    """
    create_timeline_stories_table = """
        create table if not exists timeline_stories (
            timeline_id int not null,
            story_id int not null,
            constraint fk_timeline_id foreign key (timeline_id) references timelines(id),
            constraint fk_story_id foreign key (story_id) references stories(id),
            primary key (timeline_id, story_id)
        )
    """
    create_timeline_keywords_table = """
        create table if not exists timeline_keywords (
            timeline_id int not null,
            keyword_id int not null,
            constraint fk_timeline_id foreign key (timeline_id) references timelines(id),
            constraint fk_keyword_id foreign key (keyword_id) references keywords(id),
            primary key (timeline_id, keyword_id)
        )
    """

    db.run_sql_no_return(create_providers_table)
    db.run_sql_no_return(create_articles_table)
    db.run_sql_no_return(create_article_embeddings_table)
    db.run_sql_no_return(create_stories_table)
    db.run_sql_no_return(create_story_articles_table)
    db.run_sql_no_return(create_keywords_table)
    db.run_sql_no_return(create_story_keywords_table)
    db.run_sql_no_return(create_story_embeddings_table)
    db.run_sql_no_return(create_images_table)
    db.run_sql_no_return(create_digests_table)
    db.run_sql_no_return(create_digest_rundowns_table)
    db.run_sql_no_return(create_timelines_table)
    db.run_sql_no_return(create_timeline_events_table)
    db.run_sql_no_return(create_timeline_stories_table)
    db.run_sql_no_return(create_timeline_keywords_table)
    print("Created tables")
    providers = pd.read_csv("./db/providers.csv")
    for _, row in providers.iterrows():
        provider_exists_query = "select exists(select 1 from providers where name = %s)"
        provider_exists = db.run_sql(provider_exists_query, (row["name"],))
        if not provider_exists[0][0]:
            db.insert_row("providers", dict(row))
            print(f"Inserted provider {row['name']}")
    print("Done")


if __name__ == "__main__":
    main()
