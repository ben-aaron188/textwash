# Textwash

Textwash is an automated text anonymization tool written in Python. The tool can be used to anonymize unstructured text data. To achieve this, Textwash identifies and extracts personally-identifiable information (e.g., names, dates) from text and replaces the identified entities with a generic identifier (e.g., Jane Doe is replaced with PERSON_FIRSTNAME_1 PERSON_LASTNAME_1).

## Quick start guide

Textwash is built in Python3. To run the software, it is recommended to first create an Anaconda environment and install the required dependencies.

    $ conda create -n textwash python=3.7
    $ conda activate textwash
    $ pip install -r requirements.txt

Additionally, you need to download the trained model file from [here](https://drive.google.com/file/d/1DR5SfB-xvVxXl5m4nGnSz4kri1mDOuUa/view?usp=sharing). Once you have downloaded the `model.pth`, move it into the `data` directory.

## Using Textwash

Textwash can be used to anonymize **txt** files. To do this, run `anon.py` by providing the path to the input files `--input_dir` and the corresponding path to the output folder `--output_dir`. For example, running

    $ python3 anon.py --input_dir examples --output_dir anonymized_examples --cpu

anonymizes the example texts in the `examples` directory and writes the anonymized files to a new directory called `anonymized_examples`.

Textwash works best when running on a GPU. If no GPU is available, you should use the `--cpu` flag as in the snippet above. If you have a GPU, remove the `--cpu` flag and Textwash will resort to `pytorch` with `CUDA` support.


## Who can use Textwash

Textwash is developed with non-profit open science principles. If you are a researcher, a research organization, working in the public sector or a non-profit organization, you are free to use this software. Please make sure you cite our work as follows:

(to do with DOI)

If you intend to use the current software commercially without our consent, please be advised that this software is released under the [GNU General Public License 3 (GPL-3.0)](https://www.gnu.org/licenses/gpl-3.0.en.html).

> You may copy, distribute and modify the software as long as you track changes/dates of in source files and keep modifications under GPL. You can distribute your application using a GPL library commercially, but you must also provide the source code.


## Questions and Comments

Please open a GitHub Issue if you have any questions or remarks.