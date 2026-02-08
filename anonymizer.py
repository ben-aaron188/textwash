import re
import string
from copy import deepcopy
from utils import decode_outputs


class Anonymizer:
    def __init__(self, config, classifier):
        self.config = config
        self.classifier = classifier

        with open(self.config.path_to_months_file, "r") as f:
            self.months = [m.strip() for m in f.readlines()]

        with open(self.config.path_to_written_numbers_file, "r") as f:
            self.written_numbers = [w.strip() for w in f.readlines()]

        self.valid_surrounding_chars = [
            ".", ",", ";", "!", ":", "\n", "’", "‘", "'", '"', "?", "-"
        ]

        self._strip_chars = string.punctuation + "’‘“”"

    def _normalize_whitespace_preserve_newlines(self, text: str) -> str:
        # Keep exact newline positions by processing line-by-line
        lines = text.splitlines(keepends=True)
        out = []
        for line in lines:
            # Separate content from newline so we preserve \n / \r\n exactly
            if line.endswith("\r\n"):
                content, nl = line[:-2], "\r\n"
            elif line.endswith("\n"):
                content, nl = line[:-1], "\n"
            else:
                content, nl = line, ""

            # Collapse runs of spaces/tabs inside the line, but keep leading indentation
            leading_ws = re.match(r"^[ \t]*", content).group(0)
            rest = content[len(leading_ws):]
            rest = re.sub(r"[ \t]+", " ", rest)

            # Remove trailing whitespace at end of line (common cleanup, doesn't affect blank lines)
            cleaned = (leading_ws + rest).rstrip(" \t")

            out.append(cleaned + nl)

        # Optional: trim only outer whitespace, but keep internal blank lines exactly
        return "".join(out).strip()

    def get_identifiable_tokens(self, text_input):
        predictions = decode_outputs(
            self.classifier(text_input), model_type=self.config.model_type
        )

        entities = {}
        for p in predictions:
            if p["entity"] == "NONE":
                continue

            raw = p["word"]
            if not raw or len(raw) <= 1:
                continue

            cleaned = raw.strip(self._strip_chars)

            if len(cleaned) > 1 and cleaned.isalnum():
                entities.setdefault(cleaned, p["entity"])

        return entities

    def replace_identified_entities(self, entities, anon_input_seq, entity2generic):
        for phrase, _ in sorted(entities.items(), key=lambda x: len(x[0]), reverse=True):
            if len(phrase) > 1 or phrase.isalnum():
                try:
                    escaped = re.escape(phrase)
                    repl = entity2generic[phrase]

                    for char in self.valid_surrounding_chars:
                        anon_input_seq = re.sub(
                            rf"(?<!\w){escaped}(?={re.escape(char)})",
                            repl,
                            anon_input_seq,
                        )

                    anon_input_seq = re.sub(
                        rf"(?<!\w){escaped}(?!\w)",
                        repl,
                        anon_input_seq,
                    )

                except re.error:
                    anon_input_seq = anon_input_seq.replace(phrase, entity2generic[phrase])

        return anon_input_seq

    def get_entity_type_mapping(self, entities):
        entity2generic_c = {v: 1 for _, v in entities.items()}
        entity2generic = {}

        for phrase, entity_type in entities.items():
            entity2generic[phrase] = "{}_{}".format(
                entity_type, entity2generic_c[entity_type]
            )

            entity2generic_c[entity_type] += 1

        return entity2generic

    def replace_numerics(self, anon_input_seq):
        # https://pythonexamples.org/python-regex-extract-find-all-the-numbers-in-string/
        all_numeric = list(set(re.findall("[0-9]+", anon_input_seq)))
        numeric_map = {k: "NUMERIC_{}".format(v + 1) for v, k in enumerate(all_numeric)}

        for k, v in sorted(numeric_map.items(), key=lambda x: int(x[0]), reverse=True):
            anon_input_seq = re.sub(
                "[^NUMERIC_0-9+]{}".format(k), " {}".format(v), anon_input_seq
            )

        return anon_input_seq

    def replace_pronouns(self, anon_input_seq):
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
            "mr.": "MR/MS",
            "mrs.": "MR/MS",
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
            # start-of-string cases (keep as you had, but no extra spaces needed)
            anon_input_seq = re.sub(rf"^(?i:{re.escape(k)})(?=\s)", v, anon_input_seq)

            # surrounded by non-word chars, preserving both sides
            # (?<!\w) and (?!\w) behave like "word boundaries" but work nicely with punctuation/newlines
            anon_input_seq = re.sub(
                rf"(?<!\w)(?i:{re.escape(k)})(?!\w)",
                v,
                anon_input_seq,
            )

        return anon_input_seq


    def replace_numbers_and_months(self, anon_input_seq):
        entity2generic_c = {"DATE": 1, "NUMERIC": 1}
        entity2generic = {}

        spl = re.split(r"[ ,.-]", anon_input_seq)

        for word in spl:
            if word.lower() in self.written_numbers and word not in entity2generic:
                entity2generic[word] = f"NUMERIC_{entity2generic_c['NUMERIC']}"
                entity2generic_c["NUMERIC"] += 1

        for word in spl:
            if word.lower() in self.months and word not in entity2generic:
                entity2generic[word] = f"DATE_{entity2generic_c['DATE']}"
                entity2generic_c["DATE"] += 1

        for phrase, replacement in sorted(entity2generic.items(), key=lambda x: len(x[0]), reverse=True):
            escaped = re.escape(phrase)
            anon_input_seq = re.sub(
                rf"(?<!\w){escaped}(?!\w)",
                replacement,
                anon_input_seq,
            )

        return anon_input_seq


    def anonymize(self, input_seq, selected_entities=None):
        orig_input_seq = deepcopy(input_seq)

        entities = self.get_identifiable_tokens(deepcopy(input_seq))

        # Filter entities if necessary (entities is a dict: {phrase: label})
        if selected_entities:
            entities = {
                phrase: label
                for phrase, label in entities.items()
                if label in selected_entities
            }

        entity2generic = self.get_entity_type_mapping(entities)

        anon_input_seq = re.sub(r"https*://\S+", "URL", orig_input_seq)

        anon_input_seq = self.replace_identified_entities(
            entities, orig_input_seq, entity2generic
        )

        anon_input_seq = self.replace_numerics(anon_input_seq)
        anon_input_seq = self.replace_pronouns(anon_input_seq)
        anon_input_seq = self.replace_numbers_and_months(anon_input_seq)
        anon_input_seq = self._normalize_whitespace_preserve_newlines(anon_input_seq)

        return anon_input_seq
