# Typhoon 24-Hour Movement Speed Statistics

## Data Source
Statistical script: `统计台风方向` (actual output is speed statistics)

## Statistical Metrics (Unit: km/h)

| Metric               | Value | Description |
|----------------------|-------|-------------|
| count                | 336   | Number of valid records |
| mean                 | 19.15 | Mean speed |
| std                  | 6.78  | Standard deviation |
| min                  | 3.44  | Minimum speed |
| 25%                  | 14.11 | First quartile |
| 50% (median)         | 18.95 | Median |
| 75%                  | 23.12 | Third quartile |
| max                  | 49.73 | Maximum speed |

## Distribution Characteristics

- **Concentration range**: Most typhoons have movement speeds between 14–23 km/h (25th to 75th percentiles).
- **Mean and median are close**: `mean ≈ 19.15`, `median ≈ 18.95`, indicating a roughly symmetric distribution with little influence from extreme values.
- **Speed range**: From a slowest of 3.44 km/h to a fastest of 49.73 km/h, showing considerable spread.
- **Standard deviation**: 6.78 km/h, indicating moderate dispersion around the mean.

> **Summary**: The dataset contains 336 records of 24‑hour typhoon movement speeds. The average speed is approximately 19 km/h, with most typhoons moving between 14–23 km/h.