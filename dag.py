from __future__ import annotations
from datetime import datetime
import json
from typing import List

from openai import OpenAI
import pendulum
import os

from airflow.decorators import task
from airflow.models.dag import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.trigger_rule import TriggerRule
from airflow.models import Variable
from airflow.models.baseoperator import chain


import cluster
import embedding
from db.db_connection import DBHandler
import scraper
import summarise



with DAG(
    dag_id="news_crunching_dag",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    schedule="@daily"
) as dag:
    
    config: dict = json.loads(Variable.get("news_crunching_config"))
    client = OpenAI(api_key=config['openai_key'])

    @task
    def check_db_connection(db_config) -> DBHandler:
        _ = DBHandler(db_config)
        return
    
    @task
    def pull_articles(config):
        return scraper.pull_articles(config)
    
    @task
    def embed_articles(db_config, client):
        return embedding.embed_articles(db_config, client)
    
    @task
    def summarise_articles(db_config, client):
        return summarise.summarise_articles(db_config, client)
    
    @task
    def cluster_articles(db_config, client):
        return cluster.cluster_articles(db_config, client)
    
    check_db_connection_task = check_db_connection(config['db'])
    pull_articles_tasks = []
    for feed, url in config['rss'].items():
        single_feed_config = config.copy()
        single_feed_config['rss'] = {feed: url}
        pull_articles_tasks.append(
            PythonOperator(task_id=f'pull_{feed.replace(" ", "_")}', python_callable=scraper.pull_articles, op_args=[config])
        )
    # embed_articles_task = embed_articles(config['db'], client)
    # summarise_articles_task = summarise_articles(config['db'], client)
    embed_articles_task = PythonOperator(task_id='embed', python_callable=embedding.embed_articles, op_args=[config['db'], client], trigger_rule=TriggerRule.ALL_SUCCESS)
    summarise_articles_task = PythonOperator(task_id='summarise', python_callable=summarise.summarise_articles, op_args=[config['db'], client], trigger_rule=TriggerRule.ALL_SUCCESS)
    cluster_articles_task = PythonOperator(task_id='cluster', python_callable=cluster.cluster_articles, op_args=[config['db'], client], trigger_rule=TriggerRule.ALL_SUCCESS)
    # cluster_articles_task = cluster_articles(config['db'], client)

    check_db_connection_task >> pull_articles_tasks >> embed_articles_task >> cluster_articles_task
    pull_articles_tasks >> summarise_articles_task >> cluster_articles_task
