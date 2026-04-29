```
TyphoonAnalysis_GitHub/
│
├── Analysis_1.0-Linear/          # Linear trend analysis (direction + speed)
│   │
│   ├── data/                     # Raw data
│   │   └── CMA/                  # Store CH1980BST.txt ~ CH2024BST.txt
│   │
│   ├── code/                     # All Python scripts
│   │   ├── Directional distribution + speed trend.py
│   │   ├── NW direction proportion trend (output).py
│   │   ├── Directional statistics 24 hours before landfall.py
│   │   ├── Movement speed statistics in the 24 hours before landfall.py
│   │
│   ├── output/                   # Output data tables and analysis results
│   │   ├── csv_sheet/
│   │   │   ├── df_avg_data_per_typhoon.csv      # Summary of average movement speed and dominant direction characteristics in the 24 hours before landfall
│   │   │   ├── df_landfall_points_schemeB.csv   # Landfall point dataset
│   │   │   ├── df_pre_landfall.csv              # Collection of trajectory within 24 hours before landfall
│   │   │   ├── df_region_filtered.csv           # Preliminary screening of datasets in the southeast coastal area
│   │   │
│   │   ├── figures/
│   │   │   ├── NW Directional Ratio Trend_1980-2024.png
│   │   │   ├── Directional distribution_1980-2024.png
│   │   │   ├── Movement speed trend_1980-2024.png
│   │   │
│   │   ├── result_summary/
│   │       ├── NW direction proportion trend (output).md
│   │       ├── Directional distribution + speed trend (output).md
│   │       ├── Directional statistics 24 hours before landfall(output).md
│   │       ├── Movement speed statistics in the 24 hours before landfall(output).md
│   │
│   └── README(English).md
│
└── (Other analysis modules such as Analysis_2.0-EEMD)
```