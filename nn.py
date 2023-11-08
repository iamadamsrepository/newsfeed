from dataclasses import dataclass
from typing import Any, Dict, List
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline

@dataclass
class KeyTerms:
    terms: List[str]
    types: Dict[str, str] # key: term, val: type
    # TODO: raw_output: Optional[Dict[str, list]] # key: term, val: raw output from pipe

class KeyTermExtractor:
    def __init__(self) -> None:
        tokenizer = AutoTokenizer.from_pretrained("dslim/bert-large-NER")
        model = AutoModelForTokenClassification.from_pretrained("dslim/bert-large-NER")
        self.ner_pipe = pipeline("ner", model=model, tokenizer=tokenizer, device=-1)

    def __call__(self, text: str) -> KeyTerms:
        # https://huggingface.co/dslim/bert-large-NER
        # Building KeyTerms together from output
        # Abbreviation 	Description
        # O         Outside of a named entity
        # B-MIS 	Beginning of a miscellaneous entity right after another miscellaneous entity
        # I-MIS 	Miscellaneous entity
        # B-PER 	Beginning of a person’s name right after another person’s name
        # I-PER 	Person’s name
        # B-ORG 	Beginning of an organization right after another organization
        # I-ORG 	organization
        # B-LOC 	Beginning of a location right after another location
        # I-LOC 	Location
        # Ex ner_pipe output: []
        terms = []
        types = {}
        current_keyterm = ''
        current_type = None
        for i in self.ner_pipe(text):
            if i['entity'][0] == 'B':
                if current_keyterm:
                    terms.append(current_keyterm)
                    types[current_keyterm] = current_type
                current_keyterm = i['word']
                current_type = i['entity'][2:]
            else:
                if not current_type == i['entity'][2:]:
                    raise ValueError("should be same type")
                current_keyterm += i['word'][2:]
        if current_keyterm:
            terms.append(current_keyterm)
            types[current_keyterm] = current_type
        return KeyTerms(terms, types)

# from rss import *

# k = KeyTermExtractor()
# r = RSSFeeds(urls)
# o = {}
# for e in r.entries:
#     o[e.title] = k(e.title)
...