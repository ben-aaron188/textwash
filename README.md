# Textwash

Textwash is an automated text anonymisation tool written in Python. The tool can be used to anonymise unstructured text data. To achieve this, Textwash identifies and extracts personally-identifiable information (e.g., names, dates) from text and replaces the identified entities with a generic identifier (e.g., Jane Doe is replaced with PERSON_FIRSTNAME_1 PERSON_LASTNAME_1).


## Why is this software special?

Textwash was designed to be a tool that meets the highest standards that we have for text anonymisation. The following principles guided our development decisions:

- **Complete and transparent evaluation:** you can find a full empirical evaluation of this tool in the paper linked below. We put the tool to various tests and show what it can(not) do -  this includes a motivated intruder test where humans try to re-identify persons from Textwash-anonymised documents.
- **Data never the your system:** at no point does the Textwash tool require you to upload (text) data or use an API. The tool is entirely functional offline (you can try it by switching off your Internet connection). This feature is essential to avoid any data leakage or possible risks for your data.
- **Open source:** the code base is open source and can be inspected, used adn modified in line with the [GNU General Public License 3 (GPL-3.0)](https://www.gnu.org/licenses/gpl-3.0.en.html). We do this because we think it is essential that you know what this tool does.
- **Learning-based anonymisation:** since the information that can reveal personal data is complex, we are not using a dictionary-based approach (e.g., looking up keywords in a static database). Instead, the core of Textwash is a machine learning model that assigns category probabilities to phrases and anonymises them accordingly.

### Note for researchers/organisations/other users

We would be glad if Textwash is helpful to you. But even if you prefer to use another tool, we strongly encourage you to ask the developers to provide you _as the bare minimum_ with (i) an evaluation of their tool that shows empirically what it can and cannot do (you can even point them to our evaluation approach and ask them to show how their tool performs on our evaluation dataset), and (ii) reasons why they require you to send your data to online services or an API (you should never do this, nor does a good software necessitate this).

If they refuse to provide this, you should be skeptical.


### Note for commercial anonymisation tools

We have looked hard to find a tool that is as transparent, open and data-averse (as in: not unnecessarily collecting data) as ours. We did not find any.

If you have a tool that meets these requirements, we would be glad to promote it and list it here.If you think your tool is better, we would love to see your evaluation results - you can use all the data we used and we'd be happy to assist with setting up the human intruder evaluation.


## Quick start guide

Textwash is built in Python3. To run the software, it is recommended to first create an Anaconda environment and install the required dependencies. For details on how to get and install Anaconda, click [here](https://www.anaconda.com/products/distribution).

    $ conda create -n textwash python=3.7
    $ conda activate textwash
    $ pip install -r requirements.txt

Additionally, you need to download the trained model file from [here](https://drive.google.com/file/d/1DR5SfB-xvVxXl5m4nGnSz4kri1mDOuUa/view?usp=sharing). Once you have downloaded the `model.pth`, move it into the `data` directory.

## Using Textwash

Textwash can be used to anonymise **txt** files. To do this, run `anon.py` by providing the path to the input files `--input_dir` and the corresponding path to the output folder `--output_dir`. For example, running

    $ python3 anon.py --input_dir examples --output_dir anonymised_examples --cpu

anonymises the three example texts in the `examples` directory. In doing so, Textwash loads the downloaded model into memory, then automatically anonymises the inputs and writes the anonymised files to the provided output folder `anonymised_examples`.

Textwash works best when running on a GPU. If no GPU is available, you should use the `--cpu` flag as in the snippet above. If you have a GPU, remove the `--cpu` flag and Textwash will resort to `pytorch` with `CUDA` support.


## Who can use Textwash?

Textwash is developed with non-profit open science principles. If you are a researcher, a research organization, working in the public sector or a non-profit organization, you are free to use this software. Please make sure you cite our work as follows:

(to do with DOI)

If you intend to use this software commercially without our consent, please be advised that this software is released under the [GNU General Public License 3 (GPL-3.0)](https://www.gnu.org/licenses/gpl-3.0.en.html).

> You may copy, distribute and modify the software as long as you track changes/dates of in source files and keep modifications under GPL. You can distribute your application using a GPL library commercially, but you must also provide the source code.


## Who developed Textwash?

Textwash is a multi-year project that is led by Maximilian Mozes (University College London) and Bennett Kleinberg (Tilburg University and University College London).

The work is supported by the [SAGE Concept Grant](https://www.youtube.com/watch?v=T9pRRn2DrMY) and we are currently developing it further with a grant from the Dutch Research Council (NWO).

## Questions and Comments

Please open a GitHub Issue if you have any questions or remarks.