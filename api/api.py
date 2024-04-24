from dataclasses import dataclass, asdict
import json
from typing import Dict, List
from fastapi import FastAPI
import datetime as dt
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

from db_connection import DBHandler

@dataclass
class ClusterDBOut:
    c_id: int
    c_ts: dt.datetime
    c_title: str
    c_summary: str 
    a_id: int
    a_ts: dt.datetime
    a_feed: str
    a_title: str
    a_url: str


@dataclass
class Article:
    id: int
    ts: dt.datetime
    feed: str
    title: str
    url: str


@dataclass
class Cluster:
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

# @app.get("/")
# async def root():
#     return {"message": "Hello World"}

@app.get("/stories")
async def stories():
    db_config = json.load(open("./config.json"))["db"]
    db = DBHandler(db_config)
    db_out = [ClusterDBOut(*i) for i in db.run_sql("""
        select c.id, c.ts, c.title, c.summary, 
        a.id, a.ts, a.feed, a.title, a.url
        from cluster_articles ca
        left join clusters c
        on ca.cluster_id = c.id
        left join articles a
        on ca.article_id = a.id
    """)]
    clusters_dict: Dict[int, Cluster] = {}
    for c in db_out:
        article = Article(*list(asdict(c).values())[-5:])
        if c.c_id in clusters_dict:
            clusters_dict[c.c_id].articles.append(article)
        else:
            cluster = Cluster(*list(asdict(c).values())[:4], [article])
            clusters_dict[cluster.id] = cluster
    return list(clusters_dict.values())

handler = Mangum(app)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)