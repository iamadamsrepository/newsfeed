import asyncio
import datetime as dt
import json
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
    a_id: int
    a_ts: dt.datetime
    a_title: str
    a_subtitle: str
    a_url: str
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
    provider: str
    provider_url: str
    provider_favicon: str


@dataclass
class Story:
    id: int
    ts: dt.datetime
    title: str
    summary: str
    articles: List[Article]


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
                select c.id, c.ts, c.title, c.summary, 
                a.id, a.ts, a.title, a.subtitle, a.url,
                p.name, p.url, p.favicon_url
                from story_articles ca
                left join stories c
                on ca.story_id = c.id
                left join articles a
                on ca.article_id = a.id
                left join providers p
                on a.provider_id = p.id
                where c.digest_id = {digest_id}
            """
        )
    ]
    stories: Dict[int, Story] = {}
    for s in db_out:
        article = Article(*list(asdict(s).values())[-8:])
        if s.s_id in stories:
            stories[s.s_id].articles.append(article)
        else:
            story = Story(*list(asdict(s).values())[:4], [article])
            stories[story.id] = story
    return list(stories.values())


async def fetch_stories_loop():
    global stories
    while True:
        stories = await fetch_stories()
        await asyncio.sleep(600)


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(fetch_stories_loop())


@app.get("/stories")
async def stories() -> list[Story]:
    return stories


@app.get("/story/{story_id}")
async def story(story_id: int) -> Story:
    return next(s for s in stories if s.id == story_id)


handler = Mangum(app)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
