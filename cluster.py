from functools import cached_property
import json
import math
from typing import Dict, List, Tuple, TypeAlias, Union
import numpy as np
from openai import OpenAI
from openai.types.chat.chat_completion import ChatCompletion
from scipy.cluster.hierarchy import dendrogram, linkage, cut_tree
from matplotlib import pyplot as plt
from collections import namedtuple
from sklearn.metrics.pairwise import cosine_similarity
import datetime as dt

from db.db_connection import DBHandler


ArticleInfo = namedtuple("ArticleInfo", ["id", "ts", "title", "subtitle", "provider", "embedding", "summary"])

class Cluster:
    def __init__(self, child_1, child_2, distance: float, total_articles: int) -> None:
        self.branches: List[Union[Cluster, ArticleInfo]] = [child_1, child_2]
        self.distance: float = distance
        self.total_articles: int = total_articles
        self.parent: Cluster = None
        for c in filter(lambda l: isinstance(l, Cluster), self.branches):
            c.parent = self
        self.sub_clusters: list = None
        self.headline: str = None
        self.summary: str = None

    @cached_property
    def articles(self) -> List[ArticleInfo]:
        articles = []
        for b in self.branches:
            if isinstance(b, ArticleInfo):
                articles.append(b)
            else:
                articles += b.articles
        assert len(articles) == self.total_articles
        return articles
    
    @cached_property
    def titles(self) -> List[str]:
        return [a.title for a in self.articles]
    
    def print_articles(self):
        if self.headline:
            raise NotImplementedError
        else:
            for a in self.articles:
                print(" - ", a.provider, " - ", a.title)
            print(f"{self.score:.3f}")
            print("Parent: ", self.parent)
            for a in self.parent.articles:
                print(" - ", a.provider, " - ", a.title)
            if self.parent.parent:
                print(f"{self.parent.score:.3f}")
            else:
                print('no grandparent')
            print('\n')
    
    @property
    def score(self) -> float:
        # No need to keep a cluster of entire input
        if not self.parent: 
            return -1

        return self.parent.distance / self.distance / (self.total_articles ** (1/3))

    
    @property
    def db_dict(self) -> dict:
        return {
            "ts": dt.datetime.now(),
            "title": self.headline,
            "summary": self.summary
        }

def filter_clusters(clusters: Dict[int, Cluster], n_clusters: int = 12) -> List[Cluster]:
    ordered_by_score = sorted(clusters.values(), reverse=True, key=lambda c: c.score)
    return ordered_by_score[:n_clusters]


def make_distance_matrix(embeddings: List[List[float]]) -> np.array:
    sim_matrix = cosine_similarity(embeddings, embeddings)
    dist_matrix = 1 - sim_matrix
    return dist_matrix


def make_cluster_map(articles: List[ArticleInfo], dist_matrix: np.array, with_plt=False) -> Dict[int, Cluster]:
    Z = linkage(dist_matrix, method='ward')
    if with_plt:
        fig = plt.figure(figsize=(30, 10))
        dn = dendrogram(Z, orientation='right', labels=[a.title for a in articles])
        plt.show()
    
    n = len(dist_matrix)
    n_clusters = 0
    clusters = {}
    for cluster in Z:
        in_1, in_2, dist, tot = tuple(cluster)
        in_1, in_2, tot = int(in_1), int(in_2), int(tot)
        if in_1 < n:
            # Its a leaf
            child_1: ArticleInfo = articles[in_1]
        else:
            # Its a cluster
            child_1: Cluster = clusters[in_1-n]
        if in_2 < n:
            child_2: ArticleInfo = articles[in_2]
        else:
            child_2: Cluster = clusters[in_2-n]
        clusters[n_clusters] = Cluster(child_1, child_2, dist, tot)
        n_clusters += 1
    return clusters

def get_cluster_headline_and_summary(cluster: Cluster, client: OpenAI, retries=0) -> Tuple[str, str]:
    tools = [
        {
            "type": "function",
            "function": {
                "name": "summarise_story",
                "description": "Given some information. Return a headline, up to 15 words, and summary, up to 150 words, of the news story.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "headline": {
                            "type": "string",
                            "description": "Headline for the news story up to 15 words."
                        },
                        "summary": {
                            "type": "string",
                            "description": "Summary of the news story up to 150 words.",
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
            "content": "Digest the information with a headline and summary."
        },
        {
            "role": "user",
            "content": " ".join(a.summary for a in cluster.articles)
        }
    ]
    # for article in cluster.articles:
    #     messages.append({"role": "user", "content": article.summary})
    response: ChatCompletion = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=messages,
        tools=tools,
        tool_choice="auto",
        temperature=0.3
    )
    try:
        assert len(response.choices[0].message.tool_calls) == 1
    except AssertionError:
        print("Retrying")
        if retries == 2:
            raise ValueError
        return get_cluster_headline_and_summary(cluster, client, retries+1)
    obj = json.loads(response.choices[0].message.tool_calls[0].function.arguments)
    return obj['headline'], obj['summary']

def cluster_articles(db_config: dict, client: OpenAI, dry_run=False):
    db = DBHandler(db_config)
    sql_out = db.run_sql("""
        select a.id, a.ts, a.title, a.subtitle, p.name, 
        e.embedding, s.summary
        from articles a
        left join embeddings e 
        on a.id = e.article_id
        left join article_summaries s
        on a.id = s.article_id
        left join providers p
        on a.provider_id = p.id
    """)
    articles = [ArticleInfo(a[0], a[1], a[2], a[3], a[4], eval(a[5]), a[6]) for a in sql_out]
    dist_matrix = make_distance_matrix([a.embedding for a in articles])
    all_clusters = make_cluster_map(articles, dist_matrix, with_plt=False)
    clusters: List[Cluster] = filter_clusters(all_clusters)
    if dry_run:
        for c in clusters:
            c.print_articles()
        print(f"Clusters dry run finished")
        return
    for cluster in clusters:
        cluster.headline, cluster.summary = get_cluster_headline_and_summary(cluster, client)
        db.insert_row("stories", cluster.db_dict)
        cluster_id = db.run_sql("select max(id) from stories")[0][0]
        for article in cluster.articles:
            db.insert_row("story_articles", {"story_id": cluster_id, "article_id": article.id})
        print(f"Wrote story {cluster.headline} from {cluster.total_articles} articles")

    
if __name__ == '__main__':
    config = json.load(open("./config.json"))
    client = OpenAI(api_key=config['openai_api_key'])
    cluster_articles(config['db'], client, dry_run=False)