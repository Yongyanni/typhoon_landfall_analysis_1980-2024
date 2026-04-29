# EEMD Decomposition of Typhoon Pre-landfall Movement Characteristics (1980–2024)

## Overview
This directory contains a complete analysis workflow of EEMD (Ensemble Empirical Mode Decomposition) + spectral matching + significance testing for pre-landfall (24-hour) movement characteristics (average speed and dominant direction) of typhoons making landfall on the southern/eastern coast of China from 1980 to 2024.

This analysis aims to identify multi‑timescale variations in typhoon movement speed and the proportion of NW‑dominant direction, including **long‑term trend**, **decadal oscillation (PDO)**, **ENSO cycles**, and **quasi‑decadal oscillation (QDO)**.

The data are sourced from the China Meteorological Administration (CMA) tropical cyclone best track dataset.

## Data Source
- **Provider**: China Meteorological Administration (CMA)
- **Dataset**: CMA Tropical Cyclone Best Track Data
- **Time Range**: 1980–2024
- **Access URL**: [http://tcdata.typhoon.org.cn/](http://tcdata.typhoon.org.cn/)
> The data used in this directory come from the output of Analysis_1.0: `df_avg_data_per_typhoon.csv` (summary table of average pre‑landfall speed and dominant direction per typhoon). Please place this file at `data/df_avg_data_per_typhoon.csv`.

## How to Reproduce

### Requirements
- Python 3.8+
- Required libraries: `pandas`, `numpy`, `scipy`, `matplotlib`, `emd`

Install dependencies:
```bash
pip install pandas numpy scipy matplotlib emd
Steps
Ensure the data file is in place: Analysis_2.0-EEMD/data/df_avg_data_per_typhoon.csv
```
Run the EEMD analysis of movement speed:

```bash
python code/移速序列_EEMD+频谱匹配+显著性检验.py
```
Run the EEMD analysis of NW‑dominant ratio:

```bash
python code/NW占比序列_EEMD+频谱匹配+显著性检验.py
```
All outputs are automatically saved to:
```
output/figure/

output/result_summary/
```
## Key Findings (Summary)
### 1. Movement speed series (1980–2024)
Long‑term trend: slow decrease, but not significant

PDO component: ~20–30 year cycle

ENSO component: clear 2–7 year cycles

QDO: quasi‑decadal oscillation of 8–12 years

Significance: ENSO and some QDO IMFs are significant (p < 0.05)

### 2. NW‑dominant direction ratio
Long‑term trend: slight increase in NW proportion, but not significant

PDO component: clear 20–30 year cycle

ENSO component: distinct 2–7 year cycles

QDO: ~10 year oscillation

Significance: ENSO IMF is the most significant

These results indicate that both typhoon movement direction and speed are jointly influenced by multi‑timescale climatic oscillations (ENSO / PDO / QDO), while the long‑term trends are not significant.

Directory Structure
```
Analysis_2.0-EEMD/
│
├── data/
│   └── df_avg_data_per_typhoon.csv
│
├── code/
│   ├── Speed sequence _EEMD+spectral matching+significance test.py
│   └── NW Proportion Sequence_EEMD+Spectral Matching+significance Test.py
│
├── output/
│   ├── figure/
│   │   ├── EEMD_speed_components_QDO.png
│   │   ├── IMF_significance_speed.png
│   │   ├── EEMD_NW_ratio_components_QDO.png
│   │   └── IMF_significance_NW_ratio.png
│   └── result_summary/
│       ├── Speed sequence_EEMD (output).md
│       └── NW Proportion Sequence_EEMD (Output).md
│
├── Structure.md
└── Readme_English.md
```
## License
This directory is intended to promote scientific transparency and reproducibility. The original CMA data are subject to the terms of use of the China Meteorological Administration; please cite the original data source when using them.

## Contact
If you have any questions about the code or analysis, please submit an issue or contact the author.

## Citation
If you use this code or results in your own work, please cite this repository and the original CMA data:

China Meteorological Administration (2024). Tropical Cyclone Best Track Data. http://tcdata.typhoon.org.cn/

[Yongyan Ni]. (2025). Typhoon Landing Analysis (1980–2024). GitHub. https://github.com/Yongyanni/TyphoonAnalysis_GitHub