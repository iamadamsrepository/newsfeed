from typing import List
from openai import OpenAI
from openai.types.chat.chat_completion import ChatCompletion
import json

from db.db_connection import DBHandler
from db.db_objects import ArticleRow


def get_article_summary(article: ArticleRow, client: OpenAI, retries: int = 0) -> str:
    tools = [
        {
            "type": "function",
            "function": {
                "name": "summarise_article",
                "description": "Make summary of the input article text up to 100 words.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "summary": {
                            "type": "string",
                            "description": "Summary of the article up to 100 words.",
                        }
                    },
                    "required": ["summary"],
                }
            }
        }
    ]
    messages = [
        {
            "role": "system",
            "content": "For a given article, return a summary of the article up to 100 words."
        },
        {"role": "user", "content": ' '.join(article.body.split()[:600])}
    ]
    response: ChatCompletion = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=messages,
        tools=tools,
        tool_choice="auto",
        max_tokens=2000
    )
    try:
        assert len(response.choices[0].message.tool_calls) == 1
        summary = json.loads(response.choices[0].message.tool_calls[0].function.arguments)['summary']
        assert summary
    except:
        if retries == 2:
            raise ValueError
        print('Retrying')
        return get_article_summary(article, client, retries+1)
    return summary


def summarise_articles(db_config: dict, client: OpenAI):
    db = DBHandler(db_config)
    sql_out = db.run_sql("""
        select a.*
        from articles a
        left outer join article_summaries s
        on a.id = s.article_id
        where s.article_id is null
    """)
    unsumarised_articles = [ArticleRow(*a) for a in sql_out]
    for article in unsumarised_articles:
        summary = get_article_summary(article, client)
        db.insert_row("article_summaries", {
            "article_id": article.id,
            "summary": summary
        })

if __name__ == '__main__':
    config = json.load(open("./config.json"))
    client = OpenAI(api_key=config['openai_api_key'])
    summarise_articles(config['db'], client)