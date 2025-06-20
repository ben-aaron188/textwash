import json


def assert_entities(entities, model_path):
    with open(f"{model_path}/config.json", "r") as f:
        label_map = json.load(f)["id2label"]
    available_entities = list(label_map.keys()) + ["NUMERIC", "PRONOUN"]
    available_entities = sorted(
        list(set(available_entities).difference({"NONE", "PAD"}))
    )

    entity_list = [e.strip() for e in entities.split(",")]

    for entity in entity_list:
        if entity not in available_entities:
            raise ValueError(
                "Incorrect argument --entities provided. Please ensure that all values refer to existing entities separated by comma.\n"
                "Available entities are {}.".format(", ".join(available_entities))
            )

    return entity_list


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