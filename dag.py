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
import collect
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
    
    check_db_connection_task = check_db_connection(config['db'])
    collect_articles_task = PythonOperator(task_id='collect', python_callable=collect.run_collector, op_args=[config])
    embed_articles_task = PythonOperator(task_id='embed', python_callable=embedding.embed_articles, op_args=[config['db'], client], trigger_rule=TriggerRule.ALL_SUCCESS)
    summarise_articles_task = PythonOperator(task_id='summarise', python_callable=summarise.summarise_articles, op_args=[config['db'], client], trigger_rule=TriggerRule.ALL_SUCCESS)
    cluster_articles_task = PythonOperator(task_id='cluster', python_callable=cluster.cluster_articles, op_args=[config['db'], client], trigger_rule=TriggerRule.ALL_SUCCESS)

    check_db_connection_task >> collect_articles_task >> summarise_articles_task >> embed_articles_task >> cluster_articles_task
