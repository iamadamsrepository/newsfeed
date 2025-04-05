import datetime as dt
import json
import re
from collections import namedtuple
from typing import List

import numpy as np
from hdbscan import HDBSCAN
from openai import OpenAI
from openai.types.chat.chat_completion import ChatCompletion

from db.db_connection import DBHandler

StoryInfo = namedtuple("StoryInfo", ["id", "title", "ts", "summary", "coverage", "digest_id", "embedding"])


SUPER_STORY_TIMELINE_RESPONSE_FORMAT = {
    "type": "json_schema",
    "json_schema": {
        "name": "super_story_timeline",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "subject": {
                    "type": "string",
                    "description": "2 to 5 words describing the specific story and category of the story.",
                },
                "headline": {
                    "type": "string",
                    "description": "Up to 15 words to headline the story based on the articles.",
                },
                "summary": {
                    "type": "string",
                    "description": "Up to 250 words to summarise the story based on the articles.",
                },
                "timeline_events": {
                    "type": "array",
                    "description": "A list of events in the timeline.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "date": {"type": "string", "description": "Date of the event in YYYY-MM-DD format."},
                            "event_description": {
                                "type": "string",
                                "description": "Description of the event in a single sentence up to 10 words.",
                            },
                            "story_reference": {
                                "type": "integer",
                                "description": "ID of a story that describes the event.",
                            },
                        },
                        "required": ["date", "event_description", "story_reference"],
                        "additionalProperties": False,
                    },
                },
                "keywords": {
                    "type": "array",
                    "description": "A list of up to 10 named entities relating to the story, such as names, places, events or institutions.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "keyword": {"type": "string", "description": "keyword"},
                            "type": {
                                "type": "string",
                                "enum": ["PERSON", "PLACE", "EVENT", "INSTITUTION", "CONCEPT", "OTHER"],
                            },
                        },
                        "required": ["keyword", "type"],
                        "additionalProperties": False,
                    },
                },
            },
            "required": ["subject", "headline", "summary", "timeline_events", "keywords"],
            "additionalProperties": False,
        },
    },
}


SUPER_STORY_TIMELINE_SYSTEM_MESSAGE = {
    "role": "system",
    "content": "You read several related news stories, published across many days or weeks. "
    "From the information contained in the stories you will write a subject line, headline, story summary and keywords, "
    "and then extract important events to build a timeline. "
    "The subject should be a describing specifics story and the category of the story. "
    "The headline should a newspaper-style attention-grabbing title for the story. "
    "The story summary should be a concise overview of the story. Include the most important information, and specify dates of specific events. "
    "The timeline should be a list of events, each with a date, description and story reference. "
    "Each description should be a single short sentence, the date should be in YYYY-MM-DD format, "
    "and the story reference is an ID of a story that describes the event. ",
}


def cluster_criterion(stories: List[StoryInfo]) -> bool:
    n_stories = len(stories)
    n_days = len(set(s.ts.date() for s in stories))
    most_recent_story = max(stories, key=lambda s: s.ts)
    if most_recent_story.ts < dt.datetime.now() - dt.timedelta(hours=24):
        return False
    if n_stories < 6 or n_days < 4:
        return False
    return True


def get_story_embeddings(db: DBHandler) -> list[StoryInfo]:
    sql_out = db.run_sql(
        f"""
        select s.id, s.title, s.ts, s.summary, s.coverage, d.id, e.embedding
        from stories s
        left join story_embeddings e
        on s.id = e.story_id
        left join digests d
        on s.digest_id = d.id
        where s.ts > '{(dt.datetime.now() - dt.timedelta(days=14)).strftime("%Y-%m-%d %H:%M:%S")}'
        and e.embedding is not null
    """
    )
    return [StoryInfo(a[0], a[1], a[2], a[3], a[4], a[5], eval(a[6])) for a in sql_out]


def cluster_into_super_stories(stories: List[StoryInfo]) -> List[List[StoryInfo]]:
    clusterer = HDBSCAN(min_cluster_size=3, metric="euclidean", cluster_selection_method="eom")
    labels = clusterer.fit_predict([s.embedding for s in stories])
    super_stories: list[list[StoryInfo]] = []
    for i in range(len(np.unique(labels))):
        cluster_stories = [s for s, label in zip(stories, labels) if label == i]
        if not cluster_stories:
            continue
        if cluster_criterion(cluster_stories):
            super_stories.append(cluster_stories)
    return super_stories


def generate_timeline(stories: List[StoryInfo], client: OpenAI, retries=0):
    response_format = SUPER_STORY_TIMELINE_RESPONSE_FORMAT
    messages = [
        SUPER_STORY_TIMELINE_SYSTEM_MESSAGE,
        {
            "role": "user",
            "content": "Here are the headlines and summaries of the articles about the story:\n"
            + "\n".join(
                [
                    f"{s.ts.strftime('%Y-%m-%d')}\tID:{s.id}\t{s.title}\n{s.summary}"
                    for s in sorted(stories, key=lambda s: s.ts, reverse=False)
                ]
            ),
        },
    ]
    response: ChatCompletion = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        response_format=response_format,
        temperature=1,
        max_completion_tokens=2048,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )
    try:
        assert len(response.choices) == 1
        choice = response.choices[0]
        message = choice.message
        content = json.loads(message.content)
        assert content["subject"]
        assert content["headline"]
        assert content["summary"]
        assert content["timeline_events"]
        assert content["keywords"]
        assert all(
            set(event.keys()) == {"date", "event_description", "story_reference"}
            for event in content["timeline_events"]
        )
        assert all(re.match(r"^\d{4}(-\d{2})?(-\d{2})?$", event["date"]) for event in content["timeline_events"])
        assert all(isinstance(event["story_reference"], int) for event in content["timeline_events"])
        assert all(set(keyword.keys()) == {"keyword", "type"} for keyword in content["keywords"])
    except (AssertionError, json.JSONDecodeError):
        print("Retrying")
        if retries == 2:
            raise
        return generate_timeline(stories, client, retries + 1)
    return {
        "ts": dt.datetime.now(dt.timezone.utc),
        "subject": content["subject"],
        "headline": content["headline"],
        "summary": content["summary"],
        "events": [
            {
                "event_description": event["event_description"],
                "story_id": int(event["story_reference"]),
                "date": (
                    dt.datetime.strptime(event["date"], "%Y-%m-%d").date()
                    if len(event["date"]) == 10
                    else dt.datetime.strptime(event["date"], "%Y-%m").date()
                    if len(event["date"]) == 7
                    else dt.datetime.strptime(event["date"], "%Y").date()
                ),
                "date_type": ("D" if len(event["date"]) == 10 else "M" if len(event["date"]) == 7 else "Y"),
            }
            for event in content["timeline_events"]
        ],
        "keywords": [
            {
                "keyword": keyword["keyword"],
                "type": keyword["type"],
            }
            for keyword in content["keywords"]
        ],
        "stories": [s.id for s in stories],
    }


def timeline_criterion(timeline: dict) -> bool:
    n_events = len(timeline["events"])
    earliest_date = min(event["date"] for event in timeline["events"])
    latest_date = max(event["date"] for event in timeline["events"])
    date_range = (latest_date - earliest_date).days
    if date_range < 2:
        return False
    if n_events < 3:
        return False
    if latest_date < (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=36)).date():
        return False
    return True


def print_timeline(timeline: dict):
    print("====================================")
    print(f"Timeline for {timeline['subject']}")
    print(f"Headline: {timeline['headline']}")
    print(f"Keywords: {', '.join([k['keyword'] for k in timeline['keywords']])}")
    print(f"Summary: {timeline['summary']}")
    print("Events:")
    for event in timeline["events"]:
        print(f"{event['date_type']}{event['date']} - {event['story_id']} - {event['event_description']}")
    print("\n")


def generate_timelines(super_stories: List[List[StoryInfo]], client: OpenAI) -> list[dict]:
    print(f"Generating timelines for {len(super_stories)} super stories")
    timelines = []
    for i, super_story in enumerate(super_stories):
        print(i + 1, end="\r")
        timeline = generate_timeline(super_story, client)
        if not timeline_criterion(timeline):
            continue
        print_timeline(timeline)
        timelines.append(timeline)
    return [generate_timeline(story, client) for story in super_stories]


def write_timelines_to_db(db: DBHandler, timelines: List[dict]):
    print(f"Inserting {len(timelines)} timelines into db")
    digest_id = db.run_sql("select max(digest_id) from stories")[0][0]
    for i, timeline in enumerate(timelines):
        print(i + 1, end="\r")
        db.insert_row(
            "timelines",
            {
                "ts": timeline["ts"],
                "digest_id": digest_id,
                "subject": timeline["subject"],
                "headline": timeline["headline"],
                "summary": timeline["summary"],
            },
        )
        timeline_id = db.run_sql("select max(id) from timelines")[0][0]
        for event in timeline["events"]:
            db.insert_row(
                "timeline_events",
                {
                    "timeline_id": timeline_id,
                    "story_id": event["story_id"],
                    "description": event["event_description"],
                    "date": event["date"],
                    "date_type": event["date_type"],
                },
            )
        for story_id in timeline["stories"]:
            db.insert_row("timeline_stories", {"timeline_id": timeline_id, "story_id": story_id})
        for keyword in timeline["keywords"]:
            keyword_id = db.run_sql(
                "select id from keywords where keyword = %s and type = %s", (keyword["keyword"], keyword["type"])
            )
            if not keyword_id:
                db.insert_row("keywords", {"keyword": keyword["keyword"], "type": keyword["type"]})
                keyword_id = db.run_sql("select max(id) from keywords")
            keyword_id = keyword_id[0][0]
            db.insert_row("timeline_keywords", {"timeline_id": timeline_id, "keyword_id": keyword_id})


def cluster_stories_into_timelines(db_config: dict, client: OpenAI, dry_run=False):
    print("Clustering stories into timelines")
    db = DBHandler(db_config)
    stories = get_story_embeddings(db)
    super_stories = cluster_into_super_stories(stories)
    timelines = generate_timelines(super_stories, client)
    write_timelines_to_db(db, timelines)
    print("Finished clustering stories into timelines")


if __name__ == "__main__":
    config = json.load(open("./config.json"))
    client = OpenAI(api_key=config["openai_api_key"])
    cluster_stories_into_timelines(config["railway"], client, dry_run=False)
