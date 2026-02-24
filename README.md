# Textwash

**Notice of transition to Textwash Pro**

The Textwash project evolves: to meet the growing demand for high-performance PII redaction tools, we have transitioned our core development to Textwash Pro. That shift allows us to implement significant advancements in model architecture, training data, and processing speed.  

Important: _The current repository containing the base version of Textwash **remains free and open-source**. We are committed to maintaining it with lightweight updates and PRs._

If your projects require advanced automated text anonymization with high precision, our new [Textwash Pro](https://www.textwash.eu/) offers a sophisticated anonymization software suite designed for modern data privacy needs.

We have overhauled the platform to provide an NLP anonymization tool that includes:

- updated machine-learning architecture: A complete rewrite of the core engine using bespoke NER-based anonymization (Named Entity Recognition)
- multi-language support: New models trained for probabilistic PII detection across six languages
- Enhanced PII detection: New entities for identification and replacement to ensure GDPR-compliant anonymization
- Performance & speed improvements: Substantially increased processing power for large-scale document anonymization software tasks
- User-friendly interfaces: Dedicated offline text anonymizer apps (GUIs) for both Windows and Mac (+ cloud & API & mobile)

Textwash Pro is built to help individual researchers, academic labs, and large-scale organizations (private/public sector) to anonymize qualitative data safely. The tool will enable you to meet requirements for text anonymization for studies, archiving sensitive documents, or cleaning datasets for safe LLM use.


---------


_Textwash is available for English and Dutch._

Textwash is an automated text anonymisation tool written in Python. The tool can be used to anonymise unstructured text data. To achieve this, Textwash identifies and extracts personally-identifiable information (e.g., names, dates) from text and replaces the identified entities with a generic identifier (e.g., Jane Doe is replaced with PERSON_FIRSTNAME_1 PERSON_LASTNAME_1).

## Why is this software special?

Textwash was designed to be a tool that meets the highest standards that we have for text anonymisation. The following principles guided our development decisions:

- **Complete and transparent evaluation:** you can find a full empirical evaluation of this tool in the paper linked below. We put the tool to various tests and show what it can(not) do -  this includes a motivated intruder test where humans try to re-identify persons from Textwash-anonymised documents.
- **Data never leave your system:** at no point does the Textwash tool require you to upload (text) data or use an API. The tool is entirely functional offline (you can try it by switching off your Internet connection). This feature is essential to avoid any data leakage or possible risks for your data.
- **Open source:** the code base is open source and can be inspected, used and modified in line with the [GNU General Public License 3 (GPL-3.0)](https://www.gnu.org/licenses/gpl-3.0.en.html). We do this because we think it is essential that you know what this tool does.
- **Learning-based anonymisation:** since the information that can reveal personal data is complex, we are not using a dictionary-based approach (e.g., looking up keywords in a static database). Instead, the core of Textwash is a machine learning model that assigns category probabilities to phrases and anonymises them accordingly.

### Note for researchers/organisations/other users

We would be glad if Textwash is helpful to you. But even if you prefer to use another tool, we strongly encourage you to ask the developers to provide you _as the bare minimum_ with 

- (i) an evaluation of their tool that shows empirically what it can and cannot do (you can even point them to our [TILD evaluation approach](https://arxiv.org/abs/2103.09263) and ask them to show how their tool performs on our evaluation dataset), and 
- (ii) reasons why they require you (without local alternative) to send your data to online services or an API

If they refuse to provide this, you should be skeptical.


### Note for commercial anonymisation tools

We have looked hard to find a tool that is as transparent, open and data-averse (as in: not unnecessarily collecting data) as ours. We did not find any.


## Quick start guide

Textwash is built in Python3. To run the software, it is recommended to first create an Anaconda environment and install the required dependencies. For details on how to get and install Anaconda, click [here](https://www.anaconda.com/products/distribution).

    $ conda create -n textwash python=3.9
    $ conda activate textwash
    $ pip install -r requirements.txt

Additionally, you need to download the trained model folders from [here](https://drive.google.com/file/d/1YBccngYE3lvod87TI6UIhBzrN7nY9vHS/view?usp=sharing). Once you have downloaded the tgz file, unpack it and place it in the `data` directory. **Important: the models (in `en` and `nl`) should be directly in `./data` and _not_ in the `models` parent dirctory. The relative path to the models should be `./data/en` and `./data/nl`. Otherwise, your will encounter the `Repo id must be in the form 'repo_name' ...` error.**

## Using Textwash

Textwash can be used to anonymise **txt** files. To do this, run `anon.py` by providing the `--language` ('en' for English and 'nl' for Dutch), the path to the input files `--input_dir` and the corresponding path to the output folder `--output_dir`. For example, running

    $ python3 anon.py --language en --input_dir examples --output_dir anonymised_examples --cpu

anonymises the three example texts in the `examples` directory. In doing so, Textwash loads the downloaded model into memory, then automatically anonymises the inputs and writes the anonymised files to the provided output folder `anonymised_examples`.

Textwash works best when running on a GPU. If no GPU is available, you should use the `--cpu` flag as in the snippet above. If you have a GPU, remove the `--cpu` flag and Textwash will resort to `pytorch` with `CUDA` support.

#### Entity selection
Textwash can furthermore be restricted to only consider a subset of all available entity types for anonymisation. 

The complete list of available entity types is as follows:
* ADDRESS
* DATE
* EMAIL_ADDRESS
* LOCATION
* NUMERIC
* OCCUPATION
* ORGANIZATION
* OTHER_IDENTIFYING_ATTRIBUTE
* PERSON_FIRSTNAME
* PERSON_LASTNAME
* PHONE_NUMBER
* PRONOUN
* TIME

Using the `--entities` flag, individual entity types can be selected for anonymisation. These entity types need to be separated by comma.

For example, if you would only like to anonymise the LOCATION and PERSON_FIRSTNAME entity types, run

    $ python3 anon.py --input_dir examples --output_dir anonymised_examples --cpu --entities LOCATION,PERSON_FIRSTNAME

## Examples

You can find examples of person descriptions rich in details in the `examples` directory with the corresponding anonymised versions after running it through Textwash in the `examples_anonymised` directory.


## Who can use Textwash?

Textwash is developed with non-profit open science principles. If you are a researcher, a research organization, working in the public sector or a non-profit organization, you are free to use this software. Please make sure you cite our work as follows:

Please cite our work as described in the `CITATION.cff` file at the root of the repository.

If you intend to use this software commercially without our consent, please be advised that this software is released under the [GNU General Public License 3 (GPL-3.0)](https://www.gnu.org/licenses/gpl-3.0.en.html).

> You may copy, distribute and modify the software as long as you track changes/dates of in source files and keep modifications under GPL. You can distribute your application using a GPL library commercially, but you must also provide the source code.


## Who developed Textwash?

Textwash was a multi-year project led by Bennett Kleinberg (Tilburg University and University College London).

The work was supported by a [SAGE Proof of Concept Grant](https://www.youtube.com/watch?v=T9pRRn2DrMY) and an Open Science grant from the Dutch Research Council (NWO).

Future developments of Textwash happen under Textwash Pro at: [https://www.textwash.eu/](https://www.textwash.eu/)

## Questions and Comments

Please open a GitHub Issue if you have any questions or remarks.
