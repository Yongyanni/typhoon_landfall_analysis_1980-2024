import os
import pandas as pd
import numpy as np
from scipy.stats import linregress
import matplotlib.pyplot as plt

# -----------------------------
# Fix font issues for Chinese characters (not needed for English)
# -----------------------------
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# -----------------------------
# Automatically locate CSV file (GitHub relative path)
# -----------------------------
script_dir = os.path.dirname(os.path.abspath(__file__))      # Directory of this script
project_root = os.path.dirname(script_dir)                   # Project root directory

csv_path = os.path.join(
    project_root,
    'output',
    'csv_sheet',
    'df_avg_data_per_typhoon.csv'
)

print("Reading CSV file:", csv_path)
if not os.path.exists(csv_path):
    raise FileNotFoundError(f"CSV file not found. Please check the path: {csv_path}")

# -----------------------------
# Load data
# -----------------------------
df = pd.read_csv(csv_path)

# Count total typhoons per year
yearly_count = df.groupby('YEAR').size().rename('total')

# Count NW-direction typhoons per year
yearly_nw = df[df['Dominant_Direction_24h'] == 'NW'].groupby('YEAR').size().rename('nw_count')

# Merge into one DataFrame
yearly_stats = pd.concat([yearly_count, yearly_nw], axis=1).fillna(0)
yearly_stats['nw_ratio'] = yearly_stats['nw_count'] / yearly_stats['total'] * 100

# -----------------------------
# Linear regression
# -----------------------------
years = yearly_stats.index.values
ratios = yearly_stats['nw_ratio'].values
slope, intercept, r_value, p_value, std_err = linregress(years, ratios)

print("Linear regression results for NW-direction ratio over years:")
print(f"Slope: {slope:.3f} %/year")
print(f"Intercept: {intercept:.1f} %")
print(f"R-squared: {r_value**2:.3f}")
print(f"P-value: {p_value:.3f}")

if p_value < 0.05:
    print("Conclusion: The NW-direction ratio shows a statistically significant trend over time.")
else:
    print("Conclusion: No statistically significant linear trend in NW-direction ratio over time.")

# -----------------------------
# Plotting
# -----------------------------
plt.figure(figsize=(10,5))
plt.scatter(years, ratios, color='blue', label='NW-direction ratio')
plt.plot(years, intercept + slope*years, color='red', linestyle='--', label='Linear regression')

plt.xlabel('Year')
plt.ylabel('Percentage of NW-direction Typhoons (%)')
plt.title('Interannual Trend of NW-Dominant Typhoon Ratio (1980–2024)')

plt.legend()
plt.grid(True, linestyle='--', alpha=0.6)

# -----------------------------
# Save figure (English filename)
# -----------------------------
save_path = os.path.join(
    project_root,
    'output',
    'figures',
    'NW_direction_ratio_trend_1980_2024.png'
)

plt.savefig(save_path, dpi=300, bbox_inches='tight')
print(f"Figure saved to: {save_path}")

plt.show()
