# 台风登陆前移动特征的 EEMD 分解分析 (1980–2024)

## 概述
本目录包含对 1980–2024 年中国沿海登陆台风的登陆前 24 小时移动特征（平均速度与主导方向）进行 EEMD（集合经验模态分解）+ 频谱匹配 + 显著性检验的完整分析流程。

本分析旨在识别台风移动速度与 NW 主导方向比例的 **长期趋势（Trend）**、**年代际振荡（PDO）**、**ENSO 周期**、以及 **准十年振荡（QDO）** 等多时间尺度变化特征。

数据来源为中国气象局（CMA）热带气旋最佳路径数据集。

## 数据来源
- **数据提供方**：中国气象局 (CMA)
- **数据集**：热带气旋最佳路径数据
- **时间范围**：1980–2024
- **访问地址**：[http://tcdata.typhoon.org.cn/](http://tcdata.typhoon.org.cn/)
> 本目录使用的数据来自 Analysis_1.0 的输出：`df_avg_data_per_typhoon.csv`（登陆前 24h 平均移速与主导方向统计表）。请将该文件放置于 `data/df_avg_data_per_typhoon.csv`。

## 如何重现

### 需求
- Python 3.8+
- 所需库：`pandas`、`numpy`、`scipy`、`matplotlib`、`emd`

安装依赖项:
```bash
pip install pandas numpy scipy matplotlib emd
步骤
确保数据文件已就位：Analysis_2.0-EEMD/data/df_avg_data_per_typhoon.csv
```
运行移速 EEMD 分析：

```bash
python code/移速序列_EEMD+频谱匹配+显著性检验.py
```
运行 NW 占比 EEMD 分析：
```bash
python code/NW占比序列_EEMD+频谱匹配+显著性检验.py
```
所有输出将自动保存到：
```
output/figure/

output/result_summary/
```
## 主要发现（摘要）
### 1. 移速序列（1980–2024）
长期趋势（Trend）：缓慢下降，但不显著

PDO 成分：约 20–30 年周期

ENSO 成分：2–7 年周期明显

QDO：存在 8–12 年的准十年振荡

显著性：ENSO 与部分 QDO IMF 显著（p < 0.05）

### 2. NW 主导方向比例
长期趋势：NW 占比略有上升，但不显著

PDO 成分：存在明显 20–30 年周期

ENSO 成分：2–7 年周期清晰

QDO：约 10 年周期振荡

显著性：ENSO IMF 最显著

这些结果表明：台风移动方向与速度均受到多时间尺度气候振荡（ENSO / PDO / QDO）的共同影响，而长期趋势不显著。

目录结构

```
Analysis_2.0-EEMD/
│
├── data/
│   └── df_avg_data_per_typhoon.csv
│
├── code/
│   ├── 移速序列_EEMD+频谱匹配+显著性检验.py
│   └── NW占比序列_EEMD+频谱匹配+显著性检验.py
│
├── output/
│   ├── figure/
│   │   ├── EEMD_speed_components_QDO.png
│   │   ├── IMF_significance_speed.png
│   │   ├── EEMD_NW_ratio_components_QDO.png
│   │   └── IMF_significance_NW_ratio.png
│   └── result_summary/
│       ├── 移速序列_EEMD(输出).md
│       └── NW占比序列_EEMD(输出).md
│
├── 仓库结构.md
└── Readme_中文.md
```

## 许可
本目录旨在促进科研透明度与可复现性。原始 CMA 数据受中国气象局使用条款约束，请在使用时注明来源。

## 联系方式
如对代码或分析有任何疑问，请提交 issue 或联系作者。

## 引用
如果您在自己的工作中使用此代码或结果，请引用此代码库和中国气象局的原始数据：

中国气象局 (2024). 热带气旋最佳路径数据. http://tcdata.typhoon.org.cn/

[倪雍焱]. (2025). 台风登陆分析 (1980–2024). GitHub. https://github.com/Yongyanni/TyphoonAnalysis_GitHub