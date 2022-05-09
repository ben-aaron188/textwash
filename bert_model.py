import math
from transformers import BertTokenizer, BertForTokenClassification


class BERTModel:
    def __init__(self, config):
        self.config = config

        self.tokenizer = BertTokenizer.from_pretrained(
            "bert-base-cased", do_lower_case=False
        )

        self.model = BertForTokenClassification.from_pretrained(
            "bert-base-cased",
            num_labels=self.config.num_classes,
            output_attentions=False,
            output_hidden_states=False,
        )

    def process_inference_complete(self, string):
        tokens = []
        token_sets = []

        for word in string:
            token = self.tokenizer.tokenize(word)
            tokens += token

        tokens = self.tokenizer.convert_tokens_to_ids(tokens)
        n_iter = int(math.ceil(len(tokens) / self.config.max_len))

        for idx in range(n_iter):
            tokens_sample = tokens[
                idx * self.config.max_len : (idx + 1) * self.config.max_len
            ]

            if len(tokens_sample) < self.config.max_len:
                tokens_sample += [
                    self.tokenizer.convert_tokens_to_ids(self.config.pad_token)
                ] * (self.config.max_len - len(tokens_sample))

            mask_sample = [int(x > 0) for x in tokens_sample]
            
            token_sets.append((tokens_sample, mask_sample))

        return token_sets
