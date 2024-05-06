import os
import torch
import argparse
from config import Config
from anonymizer import Anonymizer
from utils import assert_entities
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Required + optional arguments")
    parser.add_argument(
        "--cpu",
        dest="cpu",
        action="store_true",
        help="Set this flag if you want Textwash to run on CPU (rather than GPU)",
    )
    parser.add_argument(
        "--input_dir",
        dest="input_dir",
        type=str,
        required=True,
        help="Directory containing the input txt files for textwash anonymization",
    )
    parser.add_argument(
        "--output_dir",
        dest="output_dir",
        type=str,
        required=True,
        help="Output directory into which Textwash saves the anonymized files",
    )
    parser.add_argument(
        "--entities",
        dest="entities",
        type=str,
        default="",
        help="Comma-separated list of entities that should be anonymized",
    )
    parser.add_argument(
        "--language",
        dest="language",
        type=str,
        default="",
        help="The language of the documents (supports 'en' and 'nl')",
    )
    args = parser.parse_args()

    assert os.path.exists(
        args.input_dir
    ), f"Input directory {args.input_dir} does not exist!"

    if not os.path.exists(args.output_dir):
        print(f"Creating directory {args.output_dir}")
        os.makedirs(args.output_dir)

    config = Config(language=args.language)

    selected_entities = assert_entities(args.entities, config.path_to_model) if args.entities != "" else None

    tokenizer = AutoTokenizer.from_pretrained(config.path_to_model)
    model = AutoModelForTokenClassification.from_pretrained(config.path_to_model)
    classifier = pipeline("ner", model=model, tokenizer=tokenizer, device=torch.device("cuda:0" if not args.cpu else "cpu"))

    print(f"Load input data from '{args.input_dir}'")

    data = {}

    for filename in os.listdir(args.input_dir):
        if filename.endswith(".txt"):
            with open("{}/{}".format(args.input_dir, filename)) as f:
                data[filename[: filename.index(".txt")]] = f.read().strip()

    anonymizer = Anonymizer(config, classifier)

    outputs = {}

    for idx, (k, text) in enumerate(data.items()):
        anonymized = anonymizer.anonymize(
            text, selected_entities=selected_entities
        )
        outputs[k] = anonymized

        print("Anonymized {}/{}".format(idx + 1, len(data)))

    print(f"Write anonymized data to '{args.output_dir}'")

    for k, data in outputs.items():
        with open("{}/{}.txt".format(args.output_dir, k), "w+") as f:
            f.write(data)
