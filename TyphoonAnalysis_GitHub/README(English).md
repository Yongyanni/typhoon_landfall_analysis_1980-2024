# Typhoon Landfall Analysis (1980–2024)

## Overview
This repository contains all data, code, and output files for the analysis of pre‑landfall (24‑hour) movement characteristics (speed and direction) of typhoons making landfall in the South/East China coastal region from 1980 to 2024. The analysis is based on the China Meteorological Administration (CMA) best‑track dataset.

## Data Source
- **Provider**: China Meteorological Administration (CMA)
- **Dataset**: CMA Best Track Data for Tropical Cyclones
- **Time range**: 1980–2024
- **Access**: [http://tcdata.typhoon.org.cn/](http://tcdata.typhoon.org.cn/)
> The original `.txt` files (CH1980BST.txt – CH2024BST.txt) should be placed in `data/CMA/` before running the scripts.

## How to Reproduce

### Requirements
- Python 3.8+
- Required libraries: `pandas`, `numpy`, `scipy`, `matplotlib`, `seaborn`

Install dependencies:
```bash
pip install pandas numpy scipy matplotlib seaborn
Steps
Place the original data
Download the CMA best‑track files (CH1980BST.txt – CH2024BST.txt) from http://tcdata.typhoon.org.cn/ and save them into data/CMA/.
```
Run the main analysis script
```bash
python code/Directional distribution + speed trend (output).py
This script performs:

Data loading and parsing

Landfall event identification (bounding box method)

Pre‑landfall 24‑hour data extraction

Calculation of speed and direction

Generation of CSV tables and figures
```
Run the additional trend analysis 
```bash
python code/NW direction proportion trend (output).py
This script analyses the interannual trend of the proportion of NW‑dominated typhoons.
```
View summary statistics
```
output/result_summary/ contains markdown files with descriptive statistics (speed distribution, direction counts).

All generated outputs are saved in the output/ folder and can be inspected directly.
```
Key Findings (Summary)
```
Total landfall events: 336

Average pre‑landfall 24‑hour speed: 19.15 km/h
Linear trend: slope = –0.006 km/h/year, p = 0.830 → not significant

Dominant movement direction: NW (57.1%), followed by W (25.6%)

NW proportion trend (1980–2024): slope = +0.362 %/year, p = 0.068 → not significant
```
License
```
This repository is provided for academic transparency and reproducibility. The original CMA data are subject to the terms of use of the China Meteorological Administration. Please cite the original data source if you use them.
```
Contact
```
For questions or issues regarding the code, please open an issue in this repository or contact the author directly.
```
Citation 
```
If you use this code or these results in your own work, please cite this repository and the original CMA data:

China Meteorological Administration (2024). CMA Best Track Data for Tropical Cyclones. Available at: http://tcdata.typhoon.org.cn/
[Yongyan Ni]. (2026). Typhoon Landfall Analysis (1980–2024). GitHub. https://github.com/Yongyanni/TyphoonAnalysis_GitHub
