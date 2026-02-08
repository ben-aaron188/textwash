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

        # Faster membership checks
        self._months_set = {m.lower() for m in self.months}
        self._written_numbers_set = {w.lower() for w in self.written_numbers}

        self._strip_chars = string.punctuation + "’‘“”"

        self._entity_token_pat = re.compile(
            r"^[A-Za-z0-9]+(?:[’'\-\.&/][A-Za-z0-9]+)*$"
        )

        # Used for scanning word-like tokens in text for months/written numbers
        # Examples matched: "January", "twenty-five", "O'Neil"
        self._word_token_pat = re.compile(
            r"(?<!\w)([A-Za-z]+(?:[’'\-][A-Za-z]+)*)(?!\w)")

        self.pronoun_map = {
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

        # Precompile pronoun patterns once (case-insensitive)
        self._pronoun_patterns = [
            (re.compile(rf"(?<!\w){re.escape(k)}(?!\w)", re.IGNORECASE), v)
            for k, v in self.pronoun_map.items()
        ]

        # Precompile numeric matcher once
        self._num_pat = re.compile(r"(?<!\w)(\d+(?:[.,]\d+)*)(?!\w)")

        # Whitespace collapse within a line
        self._ws_collapse = re.compile(r"[ \t]+")

        # Cache compiled entity/month/number regexes for replacements
        self._entity_pat_cache: dict[str, re.Pattern] = {}
        self._entity_pat_cache_ic: dict[str, re.Pattern] = {}

    def _normalize_whitespace_preserve_newlines(self, text: str) -> str:
        lines = text.splitlines(keepends=True)
        out: list[str] = []

        for line in lines:
            if line.endswith("\r\n"):
                content, nl = line[:-2], "\r\n"
            elif line.endswith("\n"):
                content, nl = line[:-1], "\n"
            else:
                content, nl = line, ""

            m = re.match(r"^[ \t]*", content)
            leading_ws = m.group(0) if m else ""
            rest = content[len(leading_ws):]

            rest = self._ws_collapse.sub(" ", rest)
            cleaned = (leading_ws + rest).rstrip(" \t")

            out.append(cleaned + nl)

        return "".join(out)

    def get_identifiable_tokens(self, text_input):
        predictions = decode_outputs(
            self.classifier(text_input), model_type=self.config.model_type
        )

        # key by lowercase token so Tunisia/tunisia share the same replacement
        entities_by_lower: dict[str, tuple[str, str]] = {}

        for p in predictions:
            if p["entity"] == "NONE":
                continue

            raw = p["word"]
            if not raw or len(raw) <= 1:
                continue

            cleaned = raw.strip(self._strip_chars)
            if len(cleaned) <= 1:
                continue

            if not self._entity_token_pat.match(cleaned):
                continue

            key = cleaned.lower()

            # Keep first-seen surface form + label for that lowercase key
            # (stable behavior; you can change policy if you prefer)
            entities_by_lower.setdefault(key, (cleaned, p["entity"]))

        # Convert back to the {surface_form: label} dict your pipeline expects
        return {surface: label for (surface, label) in entities_by_lower.values()}


    def _get_cached_boundary_pat(self, phrase: str, ignore_case: bool = False) -> re.Pattern:
        """
        Cached boundary-safe pattern: match phrase as a standalone token.
        (?<!\w) and (?!\w) preserve punctuation/newlines around the match.
        """
        cache = self._entity_pat_cache_ic if ignore_case else self._entity_pat_cache
        pat = cache.get(phrase)
        if pat is None:
            flags = re.IGNORECASE if ignore_case else 0
            pat = re.compile(rf"(?<!\w){re.escape(phrase)}(?!\w)", flags)
            cache[phrase] = pat
        return pat

    def replace_identified_entities(self, entities, anon_input_seq, entity2generic):
        for phrase, _ in sorted(entities.items(), key=lambda x: len(x[0]), reverse=True):
            if len(phrase) > 1:
                try:
                    repl = entity2generic[phrase]
                    pat = self._get_cached_boundary_pat(phrase, ignore_case=True)
                    anon_input_seq = pat.sub(repl, anon_input_seq)
                except re.error:
                    anon_input_seq = anon_input_seq.replace(
                        phrase, entity2generic[phrase])

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

    def replace_numerics(self, anon_input_seq: str) -> str:
        """
        Replace numeric tokens with NUMERIC_1, NUMERIC_2, ... in order of appearance.
        Matches: 25, 3.14, 1,000, 1.000, 1,000.50, 1.000,50
        """

        numeric_map: dict[str, str] = {}
        counter = 1

        for m in self._num_pat.finditer(anon_input_seq):
            tok = m.group(1)
            if tok not in numeric_map:
                numeric_map[tok] = f"NUMERIC_{counter}"
                counter += 1

        def repl(m: re.Match) -> str:
            return numeric_map[m.group(1)]

        return self._num_pat.sub(repl, anon_input_seq)

    def replace_pronouns(self, anon_input_seq):
        for pat, repl in self._pronoun_patterns:
            anon_input_seq = pat.sub(repl, anon_input_seq)
        return anon_input_seq

    def replace_numbers_and_months(self, anon_input_seq: str) -> str:
        """
        (3) Improved:
        - No splitting (which misses tokens next to punctuation you didn't include).
        - Scan tokens via regex and replace using boundary-safe cached patterns.
        - Deterministic numbering in order of first appearance.
        """
        entity2generic_c = {"DATE": 1, "NUMERIC": 1}
        mapping: dict[str, str] = {}

        # Build mapping in order of appearance
        for m in self._word_token_pat.finditer(anon_input_seq):
            tok = m.group(1)
            key = tok.lower()

            if key in self._written_numbers_set and tok not in mapping:
                mapping[tok] = f"NUMERIC_{entity2generic_c['NUMERIC']}"
                entity2generic_c["NUMERIC"] += 1
            elif key in self._months_set and tok not in mapping:
                mapping[tok] = f"DATE_{entity2generic_c['DATE']}"
                entity2generic_c["DATE"] += 1

        # Replace longest first to avoid partial overlaps
        for phrase, replacement in sorted(mapping.items(), key=lambda x: len(x[0]), reverse=True):
            pat = self._get_cached_boundary_pat(phrase, ignore_case=True)
            anon_input_seq = pat.sub(replacement, anon_input_seq)

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
        anon_input_seq = self._normalize_whitespace_preserve_newlines(
            anon_input_seq)

        return anon_input_seq
