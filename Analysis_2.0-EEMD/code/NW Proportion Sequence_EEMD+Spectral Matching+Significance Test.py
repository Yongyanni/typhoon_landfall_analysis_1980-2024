import pandas as pd
import numpy as np
import emd
from scipy.fft import fft, fftfreq
import matplotlib.pyplot as plt
import os

# ============================
# 0. 设置路径（基于 GitHub 仓库结构）
# ============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # 当前 code/ 文件夹
DATA_PATH = os.path.join(BASE_DIR, "..", "data", "df_avg_data_per_typhoon.csv")
FIGURE_DIR = os.path.join(BASE_DIR, "..", "output", "figure")

os.makedirs(FIGURE_DIR, exist_ok=True)

# ============================
# 1. 读取数据
# ============================
df = pd.read_csv(DATA_PATH, encoding="utf-8")
df = df.sort_values("YEAR")

# 每年 NW 占比
nw_ratio = df.groupby("YEAR")["Dominant_Direction_24h"].apply(
    lambda x: np.mean(x == "NW")
)

years = nw_ratio.index.values
ratio = nw_ratio.values
N = len(ratio)

# ============================
# 2. 执行 EEMD
# ============================
imfs = emd.sift.ensemble_sift(ratio)
imfs = imfs.T  # 转置为 (num_imfs, N)
num_imfs = imfs.shape[0]

print(f"IMF 数量：{num_imfs}")

# ============================
# 3. 计算每个 IMF 的主周期
# ============================
def get_dominant_period(series):
    n = len(series)
    yf = np.abs(fft(series))[1:n//2]
    xf = fftfreq(n, d=1)[1:n//2]

    mask = (1/xf >= 2) & (1/xf <= 50)
    if not np.any(mask):
        return np.nan

    idx = np.argmax(yf * mask)
    return 1 / xf[idx]

periods = [get_dominant_period(imfs[i]) for i in range(num_imfs)]

for i, p in enumerate(periods):
    print(f"IMF {i}: 主周期 ≈ {p:.2f} 年")

# =========================================================
# Step 4 & 5 (V2): 精细化信号重构与显著性检验准备
# =========================================================

# --- 4.1. 基于周期的IMF归类 ---
all_indices = set(range(num_imfs))

trend_idx = [i for i, p in enumerate(periods) if p >= 40]          # >=40 年
pdo_idx   = [i for i, p in enumerate(periods) if 20 <= p < 30]     # 20–30 年
enso_idx  = [i for i, p in enumerate(periods) if 2 <= p <= 7]      # 2–7 年

categorized_indices = set(trend_idx + pdo_idx + enso_idx)
qdo_idx = list(all_indices - categorized_indices)                  # 其余全部

# 打印分类结果
print("\n--- IMF Categorization ---")
print(f"Trend components (>=40 yr): IMF {trend_idx}")
print(f"PDO components (20–30 yr): IMF {pdo_idx}")
print(f"ENSO components (2–7 yr): IMF {enso_idx}")
print(f"QDO components (other): IMF {qdo_idx}")
print("--------------------------\n")

# --- 4.2. 重构信号 ---
trend_signal = np.sum(imfs[trend_idx], axis=0) if trend_idx else np.zeros(N)
pdo_signal   = np.sum(imfs[pdo_idx], axis=0) if pdo_idx else np.zeros(N)
enso_signal  = np.sum(imfs[enso_idx], axis=0) if enso_idx else np.zeros(N)
qdo_signal   = np.sum(imfs[qdo_idx], axis=0) if qdo_idx else np.zeros(N)

# ============================
# 5. 显著性检验（保持原逻辑）
# ============================
def ar1_coefficient(x):
    return np.corrcoef(x[:-1], x[1:])[0,1]

phi = ar1_coefficient(ratio)
print("AR(1) 系数 =", phi)

def generate_ar1(phi, n):
    e = np.random.normal(0, 1, n)
    x = np.zeros(n)
    for i in range(1, n):
        x[i] = phi * x[i-1] + e[i]
    return x

MC = 1000
imf_energy_mc = np.zeros((num_imfs, MC))

for k in range(MC):
    sim = generate_ar1(phi, N)
    sim_imfs = emd.sift.ensemble_sift(sim).T
    min_imfs = min(sim_imfs.shape[0], num_imfs)
    for i in range(min_imfs):
        imf_energy_mc[i, k] = np.sum(sim_imfs[i]**2)

imf_energy_real = np.array([np.sum(imfs[i]**2) for i in range(num_imfs)])

p_values = []
for i in range(num_imfs):
    p = np.mean(imf_energy_mc[i] > imf_energy_real[i])
    p_values.append(p)
    print(f"IMF {i} 显著性 p = {p:.3f}")

# ============================
# 6. 绘图（新增 QDO 曲线）
# ============================
plt.figure(figsize=(12,8))
plt.plot(years, ratio, label="Original NW Ratio", color="black", zorder=5)
plt.plot(years, trend_signal, label="Long-term Trend (>=40 yr)", linewidth=3, color='blue')
plt.plot(years, pdo_signal, label="PDO Component (20–30 yr)", color='green')
plt.plot(years, enso_signal, label="ENSO Component (2–7 yr)", color='orange')
plt.plot(years, qdo_signal, label="Quasi-Decadal Oscillation (QDO)", color='purple', linestyle='--')

plt.legend()
plt.title("EEMD 分解：NW 方向占比变化（含 Trend / PDO / ENSO / QDO）")
plt.xlabel("Year")
plt.ylabel("NW Ratio")
plt.grid(True)
plt.savefig(os.path.join(FIGURE_DIR, "EEMD_NW_ratio_components_QDO.png"), dpi=300)
plt.show()

# ============================
# 7. IMF 显著性柱状图
# ============================
plt.figure(figsize=(10,5))
plt.bar(range(num_imfs), 1-np.array(p_values))
plt.axhline(0.95, color='red', linestyle='--', label="95% 显著性")
plt.title("IMF 显著性检验（1-p 越高越显著）")
plt.xlabel("IMF index")
plt.ylabel("1 - p")
plt.legend()
plt.savefig(os.path.join(FIGURE_DIR, "IMF_significance_NW_ratio.png"), dpi=300)
plt.show()
