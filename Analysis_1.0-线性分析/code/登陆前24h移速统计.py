import os
import pandas as pd

# 获取脚本所在目录，构建正确的文件路径
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)

# 修正后的 CSV 路径（与你仓库结构一致）
csv_path = os.path.join(project_root, 'output', 'csv_sheet', 'df_avg_data_per_typhoon.csv')

df = pd.read_csv(csv_path)
print(df['Avg_Speed_24h_kmh'].describe())
