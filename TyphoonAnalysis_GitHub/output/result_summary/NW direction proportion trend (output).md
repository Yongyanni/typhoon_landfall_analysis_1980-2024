# Interannual Trend of NW Direction Proportion (1980–2024)

## 1. Data Source

- **Input file**: `df_avg_data_per_typhoon.csv` (generated in the previous analysis step)
- **Fields**: Contains year (YEAR), dominant direction (Dominant_Direction_24h), and other information for each typhoon

## 2. Objective

Calculate the proportion of typhoons whose dominant direction is **NW** out of all landfalling typhoons each year, and test the linear trend of this proportion over years.

## 3. Linear Regression Results

| Metric | Value |
|--------|-------|
| Slope | **+0.362 %/year** |
| Intercept | -667.7 % |
| R² | 0.075 |
| p-value | **0.068** |

> **Note**: The negative intercept is due to extrapolation far from the data range and does not affect the significance of the trend.

## 4. Statistical Conclusion

- **Significance level**: α = 0.05
- **p-value = 0.068 > 0.05**  
  → **No statistically significant linear trend in NW direction proportion over years**.

Although the slope is positive (about +0.36 percentage points per year), the regression model has very low explanatory power (R² = 0.075), and the p-value is close to but not below 0.05. Therefore, we cannot reject the null hypothesis of "no trend".

## 5. Output Chart

- **File path**: `d:\下载过渡\TyphoonAnalysis\output\NW_ratio_trend.png`
- **Chart type**: Scatter plot (annual proportions) + linear regression fit line

## 6. Methodological Notes

- Only years with at least one landfalling typhoon are included in the analysis (handled automatically by the script).
- Proportion calculation: `(number of NW‑direction typhoons that year) / (total landfalling typhoons that year) × 100%`
- Regression uses Ordinary Least Squares (OLS).

---
*Report generated from the output of script `分析NW方向比例的年际变化趋势.py`*  
*Analysis time: Same as the main analysis workflow*