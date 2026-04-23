import os
import pandas as pd
import numpy as np
from scipy.stats import linregress
import matplotlib.pyplot as plt

# -----------------------------
# 解决中文显示问题（关键）
# -----------------------------
plt.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体
plt.rcParams['axes.unicode_minus'] = False    # 解决负号显示问题

# -----------------------------
# 自动定位 CSV 文件路径
# -----------------------------
script_dir = os.path.dirname(os.path.abspath(__file__))      # 当前脚本所在目录
project_root = os.path.dirname(script_dir)                   # 回到项目根目录

csv_path = os.path.join(
    project_root,
    'output',
    '方向+移速输出',
    'df_avg_data_per_typhoon.csv'
)

print("正在读取 CSV 文件：", csv_path)
if not os.path.exists(csv_path):
    raise FileNotFoundError(f"未找到 CSV 文件，请检查路径：{csv_path}")

# -----------------------------
# 读取数据
# -----------------------------
df = pd.read_csv(csv_path)

# 计算每年台风总数
yearly_count = df.groupby('YEAR').size().rename('total')

# 计算每年 NW 方向台风数量
yearly_nw = df[df['Dominant_Direction_24h'] == 'NW'].groupby('YEAR').size().rename('nw_count')

# 合并为数据框
yearly_stats = pd.concat([yearly_count, yearly_nw], axis=1).fillna(0)
yearly_stats['nw_ratio'] = yearly_stats['nw_count'] / yearly_stats['total'] * 100  # 百分比

# 线性回归（比例 vs 年份）
years = yearly_stats.index.values
ratios = yearly_stats['nw_ratio'].values
slope, intercept, r_value, p_value, std_err = linregress(years, ratios)

print("NW方向比例随年份变化的线性回归结果：")
print(f"斜率 (slope): {slope:.3f} %/year")
print(f"截距 (intercept): {intercept:.1f} %")
print(f"R-squared: {r_value**2:.3f}")
print(f"p-value: {p_value:.3f}")

if p_value < 0.05:
    print("结论：NW方向比例随年份有显著变化趋势。")
else:
    print("结论：NW方向比例随年份无显著线性趋势。")

# -----------------------------
# 绘图（方案 A）
# -----------------------------
plt.figure(figsize=(10,5))
plt.scatter(years, ratios, color='blue', label='NW方向台风比例')
plt.plot(years, intercept + slope*years, color='red', linestyle='--', label='线性回归趋势')

plt.xlabel('年份（Year）')
plt.ylabel('NW方向台风占比（%）')
plt.title('1980–2024 年 NW 主导方向台风比例的年际变化趋势')

plt.legend()
plt.grid(True, linestyle='--', alpha=0.6)

# -----------------------------
# 自动保存图像
# -----------------------------
save_path = os.path.join(project_root, 'output', 'NW_ratio_trend.png')
plt.savefig(save_path, dpi=300, bbox_inches='tight')
print(f"图像已保存至：{save_path}")

plt.show()


