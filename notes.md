Model types:
- Text embedding clustering. Find articles on the same topic from different sources based on the articles summary.
- Text summarization. Concatenate summaries of similar articles and generate one summary.
- Named entity recognition. Better tokenization of text. https://huggingface.co/dslim/bert-base-NER?text=My+name+is+Wolfgang+and+I+live+in+Berlin
- Political bias. Estimate political bias from text. Can use to check variety of POVs going into summarisation. https://huggingface.co/bucketresearch/politicalBiasBERT

Keywords:
1. Feed: one of the set of RSS feeds being digested
2. Entry: an item in the feed corresponding to an article
3. Story: subject of an entry. Multiple entries will have the same story.

Concept:
1. Select RSS feeds
2. Pull RSS data
3. For each entry:
   1. Extract key words
   2. Generate embedding
4. Cluster entries on the same story
5. For each story:
   1. Concatenate titles and subtitles of each entry into one text.
   2. Generate summary and title
   3. Provide a list of entries and link the the articles