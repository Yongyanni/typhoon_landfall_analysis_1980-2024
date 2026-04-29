```markdown
# 移速序列：EEMD + 频谱匹配 + 显著性检验 输出报告
```

## 1. 运行环境与命令

```powershell
PS D:\下载过渡\TyphoonAnalysis\result_2.0_研究分析过程> & C:\Users\DrXen\AppData\Local\Microsoft\WindowsApps\python3.12.exe d:/下载过渡/TyphoonAnalysis/result_2.0_研究分析过程/代码/移速序列_EEMD+频谱匹配+显著性检验+绘图.py
```

## 2. 运行时警告（非致命）

```
Duplicate key in file
WindowsPath('C:/Users/DrXen/AppData/Local/Packages/PythonSoftwareFoundation.Python.3.12_qbz5n2kfra8p0/LocalCache/local-packages/Python312/site-packages/matplotlib/mpl-data/matplotlibrc'),
line 814 ('font.sans-serif : Microsoft YaHei')

Duplicate key in file
WindowsPath('C:/Users/DrXen/AppData/Local/Packages/PythonSoftwareFoundation.Python.3.12_qbz5n2kfra8p0/LocalCache/local-packages/Python312/site-packages/matplotlib/mpl-data/matplotlibrc'),
line 815 ('axes.unicode_minus : False')
```

*说明：`matplotlibrc` 中存在重复键配置，但不影响程序核心计算。*

## 3. EEMD 分解结果

- **IMF 数量**：6

| IMF 分量 | 主周期（年） |
|----------|--------------|
| IMF 0    | ≈ 4.15       |
| IMF 1    | ≈ 12.00      |
| IMF 2    | ≈ 17.68      |
| IMF 3    | ≈ 48.00      |
| IMF 4    | ≈ 48.00      |
| IMF 5    | ≈ 48.00      |

### IMF 分类（基于周期）

- **Trend 分量（≥40 年）**：IMF [3, 4, 5]
- **PDO 分量（20–30 年）**：IMF []
- **ENSO 分量（2–7 年）**：IMF [0]
- **QDO 分量（其他）**：IMF [1, 2]

### 与 ENSO / PDO 匹配情况

- **ENSO IMF**：`[0]`
- **PDO IMF**：`[]`

## 4. 显著性检验（红噪声背景）

- **AR(1) 系数**：`0.18427744560031006`

| IMF 分量 | 显著性 p 值 |
|----------|-------------|
| IMF 0    | 0.00000     |
| IMF 1    | 0.00000     |
| IMF 2    | 0.00000     |
| IMF 3    | 0.00000     |
| IMF 4    | 0.00000     |
| IMF 5    | 0.00000     |

*注：p 值均小于 0.0001，表明所有 IMF 分量均通过显著性检验（相对于红噪声背景）。*

## 5. 其他运行时日志

脚本执行过程中产生了以下无关日志（来自 SogouPY 输入法的 MMKV 存储及系统过滤元素提示），不影响分析结果：

```
[I] <MMKV.cpp:166::initialize> version v2.2.4 ...
Can't find filter element
Can't find filter element
```
