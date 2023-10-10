import os
import torch
import argparse
from config import Config
from data_processor import DataProcessor
from bert_model import BERTModel
from anonymiser import Anonymiser
from utils import load_model, assert_entities

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
        help="Directory containing the input txt files for textwash anonymisation",
    )
    parser.add_argument(
        "--output_dir",
        dest="output_dir",
        type=str,
        required=True,
        help="Output directory into which Textwash saves the anonymised files",
    )
    parser.add_argument(
        "--entities",
        dest="entities",
        type=str,
        default="",
        help="Comma-separated list of entities that should be anonymised",
    )
    parser.add_argument(
        "--deny_list",
        dest="deny_list",
        type=str,
        default="",
        help="Comma-separated list of words that should not be anonymised (even if Textwash would detect them)",
    )
    parser.add_argument(
        "--allow_list",
        dest="allow_list",
        type=str,
        default="",
        help="Comma-separated list of words that should be anonymised (even if Textwash would not detect them)",
    )
    args = parser.parse_args()

    assert os.path.exists(
        args.input_dir
    ), f"Input directory {args.input_dir} does not exist!"

    if not os.path.exists(args.output_dir):
        print(f"Creating directory {args.output_dir}")
        os.makedirs(args.output_dir)

    config = Config()
    config.gpu = not args.cpu

    selected_entities = None
    allow_list = None
    deny_list = None

    if args.entities != "":
        selected_entities = assert_entities(args.entities, config.restore_path)

    if args.allow_list != "":
        allow_list = [e.strip() for e in args.allow_list.split(",")]

    if args.deny_list != "":
        deny_list = [e.strip() for e in args.deny_list.split(",")]

    data_processor = DataProcessor(config)
    config.num_classes = data_processor.label_count

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    bert_model = BERTModel(config)
    model = bert_model.model

    if config.gpu:
        model.cuda()

    print(f"Load input data from '{args.input_dir}'")

    data = {}

    for filename in os.listdir(args.input_dir):
        if filename.endswith(".txt"):
            with open("{}/{}".format(args.input_dir, filename)) as f:
                data[filename[: filename.index(".txt")]] = f.read().strip()

    model = load_model(config.load_model_path, model)
    anonymiser = Anonymiser(config, model, data_processor, device, bert_model)

    outputs = {}

    for idx, (k, text) in enumerate(data.items()):
        anonymised, orig_cut = anonymiser.anonymise(
            text,
            selected_entities=selected_entities,
            allow_list=allow_list,
            deny_list=deny_list,
        )
        outputs[k] = {"orig": orig_cut, "anon": anonymised}

        print("Anonymised {}/{}".format(idx + 1, len(data)))

    print(f"Write anonymised data to '{args.output_dir}'")

    for k, data in outputs.items():
        with open("{}/{}.txt".format(args.output_dir, k), "w+") as f:
            f.write(data["anon"])
