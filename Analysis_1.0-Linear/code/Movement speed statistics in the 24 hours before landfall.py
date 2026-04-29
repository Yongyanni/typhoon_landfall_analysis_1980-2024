import os
import pandas as pd

# Get the script directory and construct the correct file path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)

# Corrected CSV path (consistent with your repository structure)
csv_path = os.path.join(project_root, 'output', 'csv_sheet', 'df_avg_data_per_typhoon.csv')

df = pd.read_csv(csv_path)
print(df['Avg_Speed_24h_kmh'].describe())
