from sentence_transformers import SentenceTransformer
from sklearn.neighbors import NearestNeighbors

from rss import *

sentences = ["This is an example sentence", "Each sentence is converted"]

model = SentenceTransformer('sentence-transformers/bert-base-nli-mean-tokens')
embeddings = model.encode(sentences)

r = RSSFeeds(urls)
titles = [i.title for i in r.entries]
embeddings = model.encode(titles)

knn = NearestNeighbors(n_neighbors=8, metric='cosine').fit(embeddings)
dists, indices = knn.kneighbors(embeddings)
stories = {}
title_to_story = {}
for i, dis in enumerate(zip(dists, indices)):
    title = titles[i]
    print(title, ":")
    ds, inds = dis
    close = [title]
    for dist, ind in zip(ds.tolist(), inds.tolist()):
        if dist < 0.3:
            close.append(titles[ind])
    existing = [title_to_story[i] for i in close if i in title_to_story]
    if len(existing) == 0:
        story = max(stories.keys() or [-1]) + 1
        stories[story] = set(close)
        for i in close:
            title_to_story[i] = story
    elif len(existing) == 1:
        story = existing[0]
        stories[story] |= set(close)
        for i in close:
            title_to_story[i] = story
    elif len(existing) == 2:
        story = existing[0]
        t = set(close)
        for i in existing:
            t |= stories[i]
        stories[story] = t
        for i in t:
            title_to_story[i] = story


    # print('\t', f"{dist:.3f}", titles[ind])
    # print('\n')
...