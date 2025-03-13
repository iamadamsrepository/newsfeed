import asyncio
import datetime as dt
import json
import random
from dataclasses import dataclass, fields

import nltk
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from nltk.tokenize import sent_tokenize

from api.db_connection import DBHandler
from db.db_objects import ArticleRow, ProviderRow, StoryRow

nltk.download("punkt_tab")


@dataclass
class Provider:
    name: str
    url: str
    favicon_url: str
    country: str


@dataclass
class Image:
    url: str
    article_url: str
    provider: Provider


@dataclass
class Article:
    title: str
    subtitle: str
    date: dt.date
    url: str
    provider: Provider


@dataclass
class Story:
    id: int
    title: str
    ts: dt.datetime
    summary: list[str]
    coverage: list[str]
    articles: list[Article]
    images: list[Image]

    @property
    def n_articles(self) -> int:
        return len(self.articles)

    @property
    def n_providers(self) -> int:
        return len(set(a.provider.name for a in self.articles))

    @property
    def n_countries(self) -> int:
        return len(set(a.provider.country for a in self.articles))


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

ranked_stories: list[Story] = []
stories_by_id: dict[int, Story] = {}


async def fetch_stories() -> tuple[list[Story], dict[int, Story]]:
    db_config = json.load(open("./config.json"))["pi"]
    db = DBHandler(db_config)
    digest_id = db.run_sql("select max(digest_id) from stories")[0][0]
    db_out = [
        i
        for i in db.run_sql(
            f"""
                select s.*, a.*, p.*
                from story_articles sa
                left join stories s
                on sa.story_id = s.id
                left join articles a
                on sa.article_id = a.id
                left join providers p
                on a.provider_id = p.id
                where s.digest_id = {digest_id}
            """
        )
    ]
    stories: dict[int, StoryRow] = {}
    story_articles: dict[int, list[ArticleRow]] = {}
    providers: dict[int, ProviderRow] = {}
    for s in db_out:
        ls, la = len(fields(StoryRow)), len(fields(ArticleRow))  # len(fields(ProviderRow))
        story = StoryRow(*s[:ls])
        article = ArticleRow(*s[ls : la + ls])
        provider = ProviderRow(*s[la + ls :])

        if article.image_urls:
            article.image_urls = eval(article.image_urls)
        if story.id in story_articles:
            story_articles[story.id].append(article)
        else:
            story_articles[story.id] = [article]
        providers[provider.id] = provider
        stories[story.id] = story

    story_images: dict[int, list[Image]] = {}
    for story in stories.values():
        story_images[story.id] = select_image_articles(story_articles[story.id], providers)
        story_articles[story.id] = sorted(story_articles[story.id], key=article_ranking_criterion, reverse=True)

    stories_list = []
    stories_by_id = {}
    for story_out in stories.values():
        story_out: StoryRow
        story = Story(
            id=story_out.id,
            title=story_out.title,
            ts=story_out.ts,
            summary=sent_tokenize(story_out.summary),
            coverage=sent_tokenize(story_out.coverage),
            articles=[
                Article(
                    title=article.title,
                    subtitle=article.subtitle,
                    date=article.date,
                    url=article.url,
                    provider=Provider(
                        name=providers[article.provider_id].name,
                        url=providers[article.provider_id].url,
                        favicon_url=providers[article.provider_id].favicon_url,
                        country=providers[article.provider_id].country,
                    ),
                )
                for article in story_articles[story_out.id]
            ],
            images=story_images[story_out.id],
        )
        stories_list.append(story)
        stories_by_id[story_out.id] = story
    ranked_stories = sorted(stories_list, key=story_ranking_criterion, reverse=True)
    return ranked_stories, stories_by_id


def article_ranking_criterion(article: ArticleRow) -> float:
    return article.ts


def story_ranking_criterion(story: Story) -> float:
    return story.n_providers * story.n_articles


def select_image_articles(articles: list[ArticleRow], providers: dict[int, ProviderRow]) -> list[Image] | None:
    all_images: list[Image] = []
    for article in articles:
        if article.image_urls:
            all_images.extend(
                [
                    Image(
                        url=image_url,
                        article_url=article.url,
                        provider=Provider(
                            name=providers[article.provider_id].name,
                            url=providers[article.provider_id].url,
                            favicon_url=providers[article.provider_id].favicon_url,
                            country=providers[article.provider_id].country,
                        ),
                    )
                    for image_url in article.image_urls
                ]
            )
    return random.sample(all_images, min(3, len(all_images))) if all_images else None


async def fetch_stories_loop():
    global ranked_stories, stories_by_id
    while True:
        ranked_stories, stories_by_id = await fetch_stories()
        print("Fetched stories")
        await asyncio.sleep(600)


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(fetch_stories_loop())


@app.get("/stories")
async def get_stories() -> list[Story]:
    return ranked_stories


@app.get("/story/{story_id}")
async def get_story(story_id: int) -> Story:
    return stories_by_id.get(story_id)


@app.post("/refresh")
async def run_fetch_stories():
    global ranked_stories, stories_by_id
    ranked_stories, stories_by_id = await fetch_stories()
    return {"message": "stories refreshed successfully"}


handler = Mangum(app)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
