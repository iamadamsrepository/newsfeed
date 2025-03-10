import asyncio
import datetime as dt
import json
import random
from dataclasses import asdict, dataclass
from typing import Dict, List

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

from api.db_connection import DBHandler


@dataclass
class StoryDBOut:
    s_id: int
    s_ts: dt.datetime
    s_title: str
    s_summary: str
    s_coverage: str
    a_id: int
    a_ts: dt.datetime
    a_title: str
    a_subtitle: str
    a_url: str
    a_image_url: str
    p_name: str
    p_url: str
    p_favicon_url: str


@dataclass
class Article:
    id: int
    ts: dt.datetime
    title: str
    subtitle: str
    url: str
    image_url: str
    provider: str
    provider_url: str
    provider_favicon: str


@dataclass
class Story:
    id: int
    ts: dt.datetime
    title: str
    summary: str
    coverage: str
    articles: List[Article]
    image_article: Article | None = None

    @property
    def n_providers(self) -> int:
        return len(set(a.provider for a in self.articles))

    @property
    def n_articles(self) -> int:
        return len(self.articles)


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

stories: list[Story] = []


async def fetch_stories() -> list[Story]:
    db_config = json.load(open("./config.json"))["local"]
    db = DBHandler(db_config)
    digest_id = db.run_sql("select max(digest_id) from stories")[0][0]
    db_out = [
        StoryDBOut(*i)
        for i in db.run_sql(
            f"""
                select s.id, s.ts, s.title, s.summary, s.coverage,
                a.id, a.ts, a.title, a.subtitle, a.url, a.image_url,
                p.name, p.url, p.favicon_url
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
    stories: Dict[int, Story] = {}
    for s in db_out:
        article = Article(*list(asdict(s).values())[-9:])
        if s.s_id in stories:
            stories[s.s_id].articles.append(article)
        else:
            story = Story(*list(asdict(s).values())[:5], [article])
            stories[story.id] = story
    return list(stories.values())


def story_ranking_criterion(story: Story) -> float:
    return story.n_providers * story.n_articles


def select_image_article(story: Story) -> Article | None:
    articles_with_images = [article for article in story.articles if article.image_url]
    return random.choice(articles_with_images) if articles_with_images else None


async def fetch_stories_loop():
    global stories
    while True:
        stories = await fetch_stories()
        stories = sorted(stories, key=story_ranking_criterion, reverse=True)
        await asyncio.sleep(600)


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(fetch_stories_loop())


@app.get("/stories")
async def get_stories() -> list[Story]:
    for story in stories:
        story: Story
        story.image_article = select_image_article(story)
    return stories


@app.get("/story/{story_id}")
async def get_story(story_id: int) -> Story:
    return next(s for s in stories if s.id == story_id)


handler = Mangum(app)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
