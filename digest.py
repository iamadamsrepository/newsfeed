import json
from dataclasses import asdict

from openai import OpenAI
from openai.types.chat.chat_completion import ChatCompletion

from db.db_connection import DBHandler
from db.db_objects import DigestRundownRow, StoryRow
from digest_status import DigestStatus, digest_status_transition, get_incomplete_digest

RUNDOWN_TYPES = {
    "Daily News": "Up to 200 words to summarise the most important stories and information from todays news stories.",
    "Australian News": "Up to 200 words to summarise the most important Australian stories and information from todays news stories.",
    "US News": "Up to 200 words to summarise the most important American stories and information from todays news stories.",
}

DIGEST_RUNDOWN_RESPONSE_FORMAT = {
    "type": "json_schema",
    "json_schema": {
        "name": "story_title_and_summary",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                rundown_type: {
                    "type": "string",
                    "description": description,
                }
                for rundown_type, description in RUNDOWN_TYPES.items()
            },
            "required": list(RUNDOWN_TYPES.keys()),
            "additionalProperties": False,
        },
    },
}


DIGEST_RUNDOWN_SYSTEM_MESSAGE = {
    "role": "system",
    "content": "You take in text from todays news stories and generate rundowns based on given themes. "
    + str(RUNDOWN_TYPES),
}


def get_digest_description(stories: list[StoryRow]) -> str:
    d = set(story.digest_description for story in stories)
    assert len(d) == 1
    return d.pop()


def generate_rundowns(openai: OpenAI, digest_id: int, stories: list[StoryRow]) -> list[DigestRundownRow]:
    response_format = DIGEST_RUNDOWN_RESPONSE_FORMAT
    messages = [
        DIGEST_RUNDOWN_SYSTEM_MESSAGE,
        {"role": "user", "content": "\n".join(f"{story.title}\n{story.summary}\n" for story in stories)},
    ]
    response: ChatCompletion = openai.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        response_format=response_format,
        temperature=1,
        max_completion_tokens=2048,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )
    assert len(response.choices) == 1
    choice = response.choices[0]
    message = choice.message
    content: dict = json.loads(message.content)
    assert set(content.keys()) == set(RUNDOWN_TYPES.keys())
    return [
        DigestRundownRow(digest_id=digest_id, rundown_type=rundown_type, rundown=rundown)
        for rundown_type, rundown in content.items()
    ]


def print_digest_rundowns(digest_descriptin: str, digest_rundown_rows: list[DigestRundownRow]):
    print(f"For digest: {digest_descriptin}")
    for row in digest_rundown_rows:
        print(f"{row.rundown_type} Rundown")
        print(row.rundown)


@digest_status_transition(
    expected_status=DigestStatus.IMAGES_COLLECTED,
    final_status=DigestStatus.RUNDOWNS_GENERATED,
)
def process_latest_digest(db: DBHandler, openai: OpenAI, dry_run=False):
    print("Processing latest digest")
    latest_digest_id, _ = get_incomplete_digest(db)
    digest_stories: list[StoryRow] = list(
        map(lambda i: StoryRow(*i), db.run_sql(f"select * from stories where digest_id = {latest_digest_id}"))
    )
    print(f"Generating rundowns for digest {latest_digest_id} with {len(digest_stories)} stories")
    digest_rundown_rows = generate_rundowns(openai, latest_digest_id, digest_stories)
    digest_description = get_digest_description(digest_stories)
    print_digest_rundowns(digest_description, digest_rundown_rows)

    if not dry_run:
        print(f"Inserting {len(digest_rundown_rows)} rows into digest_rundowns")
        for i, row in enumerate(digest_rundown_rows):
            print(f"inserting row {i}", end="\r")
            db.insert_row("digest_rundowns", asdict(row))
    else:
        print("Dry run, not inserting rows")
    print("Done processing latest digest")


if __name__ == "__main__":
    config = json.load(open("./config.json"))
    db = DBHandler(config["railway"])
    client = OpenAI(api_key=config["openai_api_key"])
    process_latest_digest(db, client, dry_run=False)
