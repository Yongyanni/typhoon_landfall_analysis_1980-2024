import os
import pandas as pd

# 获取脚本所在目录，构建正确的文件路径
script_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(script_dir, '..', 'output', '方向+移速输出', 'df_avg_data_per_typhoon.csv')

df = pd.read_csv(csv_path)
print(df['Avg_Speed_24h_kmh'].describe())