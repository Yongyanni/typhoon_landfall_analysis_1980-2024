import os
import pandas as pd

# 获取脚本所在目录，构建正确的文件路径
script_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(script_dir, '..', 'output', '方向+移速输出', 'df_avg_data_per_typhoon.csv')

df = pd.read_csv(csv_path)

# 统计主导移动方向的频数分布
direction_counts = df['Dominant_Direction_24h'].value_counts()
print("主导移动方向频数分布：")
print(direction_counts)

# 计算百分比
direction_percent = df['Dominant_Direction_24h'].value_counts(normalize=True) * 100
print("\n主导移动方向百分比：")
print(direction_percent)

# 如需按特定顺序显示（例如：N, NE, E, SE, S, SW, W, NW）
ordered_categories = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
direction_counts_ordered = df['Dominant_Direction_24h'].value_counts().reindex(ordered_categories)
print("\n按方向顺序排列的频数分布：")
print(direction_counts_ordered)