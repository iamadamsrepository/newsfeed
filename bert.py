from typing import List, Optional, Tuple, Union
import torch
from transformers.modeling_outputs import BaseModelOutputWithPoolingAndCrossAttentions
from transformers.models.bert.modeling_bert import BertModel


class BertWithCache(BertModel):
    def __init__(self, bert: BertModel):
        self.__class__ = type(bert.__class__.__name__,
                              (self.__class__, bert.__class__),
                              {})
        self.__dict__ = bert.__dict__
        self.og_bert = bert
        self.cache = {}
    
    def forward(self, *args, **kwargs) -> Tuple[torch.Tensor] | BaseModelOutputWithPoolingAndCrossAttentions:
        input_id = hash(tuple(args[0][0].tolist()))
        if input_id in self.cache:
            output = self.cache[input_id]
        else:
            output = super().forward(*args, **kwargs)
            self.cache[input_id] = output
        return output