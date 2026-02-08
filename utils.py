import json

def assert_entities(entities: str, model_path: str):
    with open(f"{model_path}/config.json", "r") as f:
        id2label = json.load(f)["id2label"]

    available_entities = set(id2label.values())
    available_entities.update({"NUMERIC", "PRONOUN"})
    available_entities.difference_update({"NONE", "PAD"})

    entity_list = [e.strip() for e in entities.split(",") if e.strip()]

    # Normalize for case-insensitive CLI
    available_upper = {e.upper() for e in available_entities}
    normalized = []
    for e in entity_list:
        eu = e.upper()
        if eu not in available_upper:
            raise ValueError(
                "Incorrect argument --entities provided. Please ensure that all values refer to existing entities separated by comma.\n"
                "Available entities are {}.".format(", ".join(sorted(available_entities)))
            )
        # preserve canonical capitalization from available_entities
        # (find the matching one)
        canonical = next(x for x in available_entities if x.upper() == eu)
        normalized.append(canonical)

    return normalized


def decode_outputs(predicted_labels, model_type="bert"):
    entities = []
    shift_idx = 2 if model_type == "bert" else 0

    for _, elem in enumerate(predicted_labels):
        attach = False

        if model_type == "bert" and elem["word"].startswith("##"):
            attach = True

        elif model_type == "roberta" and not elem["word"].startswith("Ġ"):
            attach = True

        if attach:
            entities[-1]["word"] += elem["word"][shift_idx:]
            entities[-1]["end"] = elem["end"]
        else:
            entities.append(
                {
                    "word": elem["word"],
                    "start": elem["start"],
                    "end": elem["end"],
                    "entity": elem["entity"],
                }
            )

    if model_type == "roberta":
        for elem in entities:
            elem["word"] = elem["word"][1:]

    return entities
