import re
import torch
import torch.nn as nn
from copy import deepcopy
from utils import tokenize, get_named_entities_from_preds, get_cut_idx


class Anonymiser:
    def __init__(self, config, model, data_processor, device, bert_model):
        self.config = config
        self.model = model
        self.data_processor = data_processor
        self.device = device
        self.bert_model = bert_model

        with open(self.config.path_to_months_file) as f:
            self.months = f.readlines()
            self.months = [m.replace("\n", "") for m in self.months]

        with open(self.config.path_to_written_numbers_file) as f:
            self.written_numbers = f.readlines()
            self.written_numbers = [w.replace("\n", "") for w in self.written_numbers]

        self.valid_surrounding_chars = [
            ".",
            ",",
            ";",
            "!",
            ":",
            "\n",
            "’",
            "‘",
            "'",
            '"',
            "?",
            "-",
        ]

    def replace_identified_entities(self, entities, anon_input_seq, entity2generic):
        for phrase, _ in sorted(
            entities.items(), key=lambda x: len(x[0]), reverse=True
        ):
            try:
                for char in self.valid_surrounding_chars:
                    anon_input_seq = re.sub(
                        "[^a-zA-Z0-9]{}[{}]".format(phrase, char),
                        " {}{}".format(entity2generic[phrase], char),
                        anon_input_seq,
                    )

                anon_input_seq = re.sub(
                    "[^a-zA-Z0-9\n]{}[^a-zA-Z0-9\n]".format(phrase),
                    " {} ".format(entity2generic[phrase]),
                    anon_input_seq,
                )

                anon_input_seq = re.sub(
                    "[\n]{}".format(phrase),
                    "\n{}".format(entity2generic[phrase]),
                    anon_input_seq,
                )
            except re.error:
                anon_input_seq = anon_input_seq.replace(
                    "{}".format(phrase), "{}".format(entity2generic[phrase])
                )

        return anon_input_seq

    def anonymise(self, input_seq):
        orig_input_seq = deepcopy(input_seq)
        anon_input_seq = " {}".format(deepcopy(input_seq))
        entities = self.get_identifiable_tokens(deepcopy(input_seq))

        entities = {k: v for [k, v] in entities if k != self.config.unk_token}
        entity2generic_c = {v: 1 for _, v in entities.items()}
        entity2generic = {}

        inv = [k for k, _ in entities.items() if len(k) == 1 and not k.isalnum()]

        for ex in list(set(inv)):
            try:
                del entities[ex]
            except KeyError:
                pass

        anon_input_seq = re.sub("https*://\S+", "URL", anon_input_seq)

        for phrase, entity_type in entities.items():
            entity2generic[phrase] = "{}_{}".format(
                entity_type, entity2generic_c[entity_type]
            )
            entity2generic_c[entity_type] += 1

        unfound_entities = {}
        for phrase, entity_type in entities.items():
            if phrase not in anon_input_seq:
                if len(phrase.split(" ")) > 1:
                    for substr in phrase.split(" "):
                        unfound_entities[substr] = entity_type
                        entity2generic[substr] = entity2generic[phrase]
                else:
                    print(f"LENGTH EXCEPTION: {phrase}")

        anon_input_seq = self.replace_identified_entities(
            entities, anon_input_seq, entity2generic
        )

        anon_input_seq = self.replace_identified_entities(
            unfound_entities, anon_input_seq, entity2generic
        )

        all_numeric = list(set(re.findall("[0-9]+", anon_input_seq)))
        numeric_map = {k: "NUMERIC_{}".format(v + 1) for v, k in enumerate(all_numeric)}

        for k, v in sorted(numeric_map.items(), key=lambda x: int(x[0]), reverse=True):
            anon_input_seq = re.sub(
                "[^NUMERIC_0-9+]{}".format(k), " {}".format(v), anon_input_seq
            )

        pronoun_map = {
            "he": "PRONOUN",
            "she": "PRONOUN",
            "him": "PRONOUN",
            "his": "PRONOUN",
            "her": "PRONOUN",
            "hers": "PRONOUN",
            "himself": "PRONOUN",
            "herself": "PRONOUN",
            "mr": "MR/MS",
            "mrs": "MR/MS",
            "miss": "MR/MS",
            "ms": "MR/MS",
            "dr": "TITLE",
            "dr.": "TITLE",
            "prof": "TITLE",
            "prof.": "TITLE",
            "sir": "TITLE",
            "dame": "TITLE",
            "madam": "TITLE",
            "lady": "TITLE",
            "lord": "TITLE",
        }

        for k, v in pronoun_map.items():
            if anon_input_seq.startswith("{} ".format(k)):
                anon_input_seq = anon_input_seq.replace(
                    "{} ".format(k), "{} ".format(v), 1
                )

            if anon_input_seq.startswith("{} ".format(k.capitalize())):
                anon_input_seq = anon_input_seq.replace(
                    "{} ".format(k.capitalize()), "{} ".format(v), 1
                )

            for char in self.valid_surrounding_chars:
                anon_input_seq = re.sub(
                    "[^a-zA-Z0-9]{}[{}]".format(k, char),
                    " {}{}".format(v, char),
                    anon_input_seq,
                )
                anon_input_seq = re.sub(
                    "[^a-zA-Z0-9]{}[{}]".format(k.capitalize(), char),
                    " {}{}".format(v, char),
                    anon_input_seq,
                )

            anon_input_seq = re.sub(
                "[^a-zA-Z0-9]{}[^a-zA-Z0-9]".format(k),
                " {} ".format(v),
                anon_input_seq,
            )
            anon_input_seq = re.sub(
                "[^a-zA-Z0-9]{}[^a-zA-Z0-9]".format(k.capitalize()),
                " {} ".format(v),
                anon_input_seq,
            )

        entity2generic_c = {"DATE": 1, "NUMERIC": 1}
        entity2generic = {}

        spl = re.split("[ ,.-]", anon_input_seq)

        for word in spl:
            if word.lower() in self.written_numbers:
                try:
                    _ = entity2generic[word]
                except KeyError:
                    entity2generic[word] = "{}_{}".format(
                        "NUMERIC", entity2generic_c["NUMERIC"]
                    )
                    entity2generic_c["NUMERIC"] += 1

        for word in spl:
            if word.lower() in self.months:
                try:
                    _ = entity2generic[word]
                except KeyError:
                    entity2generic[word] = "{}_{}".format(
                        "DATE", entity2generic_c["DATE"]
                    )
                    entity2generic_c["DATE"] += 1

        for phrase, replacement in sorted(
            entity2generic.items(), key=lambda x: len(x[0]), reverse=True
        ):
            for char in self.valid_surrounding_chars:
                anon_input_seq = re.sub(
                    "[^a-zA-Z0-9]{}[{}]".format(phrase, char),
                    " {}{}".format(replacement, char),
                    anon_input_seq,
                )

            anon_input_seq = re.sub(
                "[^a-zA-Z0-9]{}[^a-zA-Z0-9]".format(phrase),
                " {} ".format(replacement),
                anon_input_seq,
            )

        return (
            re.sub(" +", " ", anon_input_seq[1:]),
            re.sub(" +", " ", orig_input_seq),
        )

    def get_identifiable_tokens(self, tokens):
        identifiable_tokens = {}
        seq_t, preds_t = [], []

        softmax = nn.Softmax(dim=2)
        tokens = tokenize(tokens)

        self.model.eval()

        token_sets = self.bert_model.process_inference_complete(tokens)

        for token_ids, masks in token_sets:
            token_ids = torch.tensor([token_ids])
            masks = torch.tensor([masks])

            if self.config.gpu:
                token_ids, masks = token_ids.to(self.device), masks.to(self.device)

            outputs = self.model(token_ids, attention_mask=masks)
            outputs = outputs[0]
            outputs = softmax(outputs)
            _, preds = torch.max(outputs, 2)
            preds = preds.cpu().detach().numpy()
            token_ids = token_ids.cpu().detach().numpy()
            seq = self.bert_model.tokenizer.convert_ids_to_tokens(token_ids[0])
            seq = seq[: get_cut_idx(seq, self.config.pad_token)]
            seq_t += seq
            preds_t += list(preds[0])

        entities = get_named_entities_from_preds(
            seq_t, preds_t, self.data_processor.label_map_rev
        )

        for [entity, entity_type] in entities:
            try:
                identifiable_tokens[entity_type].append(entity)
            except KeyError:
                identifiable_tokens[entity_type] = [entity]

        identifiable_tokens = [
            [e, t] for t, ents in identifiable_tokens.items() for e in list(set(ents))
        ]

        return identifiable_tokens
