import re
import torch
import pickle


def get_named_entities_from_preds(text, preds, label_map_rev):
    named_entities = []
    output_string = []
    output_labels = []

    for word, tag in zip(text, preds):
        if word[:2] == "##":
            output_string[-1] = output_string[-1].strip() + word[2:].strip()
        else:
            output_string.append(word)
            output_labels.append(tag)

    for idx, (token, pred) in enumerate(zip(output_string, output_labels)):
        if pred != 0:
            if idx == 0:
                named_entities.append([token, label_map_rev[pred]])
            else:
                if output_labels[idx - 1] == pred:
                    named_entities[-1][0] += " {}".format(token)
                else:
                    named_entities.append([token, label_map_rev[pred]])

    return named_entities


def tokenize(input_string):
    assert isinstance(input_string, str)
    input_string = re.sub(r"[^a-zA-Z0-9.]+", " ", input_string)
    return [x for x in input_string.split(" ")]


def load_pkl(path):
    with open(path, "rb") as f:
        data = pickle.load(f)

    return data


def get_cut_idx(string, pad):
    last_valid_idx = len(string)

    for i in reversed(range(len(string))):
        if string[i] == pad:
            last_valid_idx -= 1
        else:
            break

    return last_valid_idx


def load_model(path, model):
    checkpoint = torch.load(path, map_location=torch.device("cpu"))
    model.load_state_dict(checkpoint["model_state_dict"])
    return model
