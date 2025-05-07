# YOUth pilot privacy-friendly synthetic data
![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=fff)
![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json) 

This repository implements a pilot for creating privacy-friendly questionnaire datasets from the YOUth cohort. It is built on [metasyn](https://github.com/sodascience/metasyn) with the [disclosure control plugin](https://github.com/sodascience/metasyn-disclosure-control).

## Installation

To install the dependencies of this project, follow the following steps:

1. We use [uv](https://docs.astral.sh/uv) to manage dependencies and environments. Install it first.
2. Clone this repository.
3. Instantiate the environment by running `uv sync` from this folder.

## Synthesizing data
1. Obtain the following datasets from the YOUth study and put them in the `raw_data` folder: `CECPAQ_2.csv`, `M_DEMOGRAFY_1.csv`, `P_DEMOGRAFY_1.csv`, `P_LIFSTYLE_1_MED_STOREY.csv`, `P_LIFSTYLE_1_MEDICATIONY.csv`, `P_LIFSTYLE_1.csv`, `Q_1.csv`
2. Obtain the following metadata files and put them in the `raw_data\metadata` folder: `YOUth_baby_en_kind-metadata.csv`, `YOUth_baby_en_kind-valuelabels.csv`.
3. Create the synthetic data by running `uv run main.py`

Now, the folders `output/csv` and `output/gmf` should be populated with synthetic data and metadata, respectively:

```
📁 synthetic_youth_pilot/
├── 📖 README.md
├── 📄 analysis.py
├── 📄 main.py
├── pyproject.toml
├── uv.lock
├── 📁 raw_data/
│   ├── 📜 CECPAQ_2.csv
│   ├── 📜 M_DEMOGRAFY_1.csv
│   ├── 📜 P_DEMOGRAFY_1.csv
│   ├── 📜 P_LIFSTYLE_1.csv
│   ├── 📜 P_LIFSTYLE_1_MEDICATIONY.csv
│   ├── 📜 P_LIFSTYLE_1_MED_STOREY.csv
│   ├── 📜 Q_1.csv
│   └── 📁 metadata/
│       ├── 📜 YOUth_baby_en_kind-metadata.csv
│       └── 📜 YOUth_baby_en_kind-valuelabels.csv
└── 📁 output/
    ├── 📁 csv/
    │   ├── 📜 CECPAQ_2.csv
    │   ├── 📜 M_DEMOGRAFY_1.csv
    │   ├── 📜 P_DEMOGRAFY_1.csv
    │   ├── 📜 P_LIFSTYLE_1.csv
    │   ├── 📜 P_LIFSTYLE_1_MEDICATIONY.csv
    │   ├── 📜 P_LIFSTYLE_1_MED_STOREY.csv
    │   └── 📜 Q_1.csv
    └── 📁 gmf/
        ├── 📜 CECPAQ_2.json
        ├── 📜 M_DEMOGRAFY_1.json
        ├── 📜 P_DEMOGRAFY_1.json
        ├── 📜 P_LIFSTYLE_1.json
        ├── 📜 P_LIFSTYLE_1_MEDICATIONY.json
        ├── 📜 P_LIFSTYLE_1_MED_STOREY.json
        └── 📜 Q_1.json

5 directories, 28 files
📖README 📜Data 📄Code 📁Folder
```
_(Made with [`scitree`](https://github.com/J535D165/scitree))_

## Test analysis

This repo includes a test analysis on both the real and synthetic data to display medication use by age bracket. You can find the analysis in the file [test_analysis.py](./test_analysis.py). To run this analysis, run `uv run test_analysis.py`. It will show something like the following:

```
Paracetamol use in real data:

Age: 10 - 19 | ____ ███████████████████
Age: 20 - 29 | ____ ████████████████
Age: 30 - 39 | ____ ███████████████
Age: 40 - 49 | ____ ██████████████
Age: 50 - 59 | ____ █████████


Paracetamol use in synthetic data:

Age: 10 - 19 | 0.81 ████████████████████
Age: 20 - 29 | 0.81 ████████████████████
Age: 30 - 39 | 0.78 ███████████████████
Age: 40 - 49 | 0.74 ██████████████████
Age: 50 - 59 | 0.81 ████████████████████
```
_(numbers redacted & bars fuzzed in real data analysis for privacy)_

Three things are noteworthy here:
1. The analysis code is __exactly__ the same between the synthetic and real analyses
2. The ranges of the individual variables (age and paracetamol use) are similar
3. The relation between age and paracetamol use is removed from the synthetic data

## Contact

This is a project by the [ODISSEI Social Data Science team](https://odissei-soda.nl/). Do you have questions, suggestions, or remarks on the technical implementation? Create an issue in the issue tracker or feel free to contact [Erik-Jan van Kesteren](https://github.com/vankesteren). 

<img src="https://odissei-soda.nl/images/logos/soda_logo.svg" alt="SoDa logo" width="250px"/> 