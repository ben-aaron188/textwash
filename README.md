# Textwash

Textwash is an automated text anonymization tool written in Python. The tool can be used to anonymize unstructured text data. To achieve this, Textwash identifies and extracts personally-identifiable information (e.g., names, dates) from text and replaces the identified entities with a generic identifier (e.g., Jane Doe is replaced with PERSON_FIRSTNAME_1 PERSON_LASTNAME_1).

## Getting Started

Textwash is built in Python3. To run the software, it is recommended to first create an Anaconda environment and install the required dependencies.

    $ conda create -n textwash python=3.7
    $ conda activate textwash
    $ pip install -r requirements.txt

Additionally, you need to download the trained model file from [here](https://drive.google.com/file/d/1DR5SfB-xvVxXl5m4nGnSz4kri1mDOuUa/view?usp=sharing). Once you have downloaded the `model.pth`, move it into the `data` directory.

## Using Textwash

Textwash can be used to anonymize **txt** files. To do this, run `anon.py` by providing the path to the input files `--input_dir` and the corresponding path to the output folder `--output_dir`. For example, running

    $ python3 anon.py --input_dir examples --output_dir anonymized_examples

anonymizes the example texts in the `examples` directory.

Textwash works best when running on a GPU. If no GPU is available, you can add the `--cpu` flag.

## Questions and Comments

Please open a GitHub Issue should you have any questions or remarks.