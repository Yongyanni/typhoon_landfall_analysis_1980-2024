import pandas as pd
import os
from math import radians, sin, cos, sqrt, atan2, degrees
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import linregress
import numpy as np  # Needed for numerical operations, e.g., for handling NaN values cleanly

# Set Matplotlib to use a Chinese-friendly font if available (for Windows)
# 兼容性 (Compatibility): Windows 11 环境下，默认可能缺少支持中文的字体。
# 这里尝试使用 'SimHei' (微软雅黑) 或 'Arial Unicode MS'。
# 如果你系统中没有这些字体，图表中的中文字符可能显示为方块。
# 解决方法: 安装缺失字体，或替换为系统中已有的中文字体，例如 'Microsoft YaHei'。
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False  # Ensures minus signs display correctly


# --- Helper Function: parse_cma_track_file (Modified for robust parsing) ---
def parse_cma_track_file(filepath):
    data = []
    current_typhoon_sid = None
    current_typhoon_name = None

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:  # Skip empty lines
                continue

            # Identity (标识): 识别台风头部行，包含台风ID和名称
            # Example: 66666 0000   14 0001 8301 0 6 Sarah 20110729
            # Example: 66666 2401   38 0001 2401 0 6 EWINIAR 20250301
            if line.startswith('66666'):
                parts = line.split()
                if len(parts) >= 8:  # 确保行中包含足够的组成部分
                    typhoon_id_code_str = parts[4]  # 例如 '8301', '2401'
                    typhoon_year_prefix = typhoon_id_code_str[:2]
                    typhoon_num_suffix = typhoon_id_code_str[2:]

                    full_year = int(typhoon_year_prefix)
                    if 80 <= full_year <= 99:  # 1980-1999 年的台风
                        full_year_str = f"19{typhoon_year_prefix}"
                    elif 0 <= full_year <= 24:  # 2000-2024 年的台风
                        full_year_str = f"20{typhoon_year_prefix}"
                    else:
                        print(
                            f"Warning: Unrecognized year prefix {typhoon_year_prefix} in typhoon ID {typhoon_id_code_str} from file {filepath}. Using XXXX as year."
                        )
                        full_year_str = "XXXX"

                    current_typhoon_sid = f"{full_year_str}{typhoon_num_suffix.zfill(2)}"
                    current_typhoon_name = parts[7]  # 例如 'Sarah', 'EWINIAR'
                else:
                    print(
                        f"Warning: Header line in {filepath} has fewer than 8 parts: '{line}'. Skipping header."
                    )
                    current_typhoon_sid = None
                    current_typhoon_name = None
                    continue

            # Process (处理): 处理台风轨迹数据行
            # Example data line: 1983062300 0 140 1170 1004 10
            elif current_typhoon_sid:
                parts = line.split()
                if len(parts) >= 6:
                    try:
                        datetime_str = parts[0]  # YYYYMMDDHH (例如 '1983062300')
                        year = int(datetime_str[:4])
                        month = int(datetime_str[4:6])
                        day = int(datetime_str[6:8])
                        hour = int(datetime_str[8:10])
                        iso_time = pd.to_datetime(
                            f"{year}-{month:02d}-{day:02d} {hour:02d}:00:00"
                        )

                        type_code = int(parts[1])  # 台风类型代码
                        lat = float(parts[2]) / 10.0  # 纬度 (除以10得到真实值)
                        lon = float(parts[3]) / 10.0  # 经度 (除以10得到真实值)
                        pressure = int(parts[4])  # 中心气压
                        wind_ms = float(parts[5])  # 最大风速 (米/秒)

                        data.append(
                            [
                                current_typhoon_sid,
                                current_typhoon_name,
                                iso_time,
                                type_code,
                                lat,
                                lon,
                                pressure,
                                wind_ms,
                            ]
                        )
                    except (ValueError, IndexError) as e:
                        print(
                            f"解析轨迹数据行失败 (台风ID: {current_typhoon_sid}, 行: '{line}'), 错误: {e}"
                        )
                        continue
                else:
                    print(
                        f"Warning: Track data line for {current_typhoon_sid} has fewer than 6 parts: '{line}'. Skipping."
                    )

    if not data:
        print(f"Warning: No valid data parsed from {filepath}.")
        return pd.DataFrame()

    df_parsed = pd.DataFrame(
        data,
        columns=[
            'SID',
            'NAME',
            'ISO_TIME',
            'TYPE_CODE',
            'LAT',
            'LON',
            'PRESSURE',
            'WIND_MS',
        ],
    )
    df_parsed['YEAR'] = df_parsed['ISO_TIME'].dt.year
    df_parsed['WIND_KMH'] = df_parsed['WIND_MS'] * 3.6  # 将风速从 m/s 转换为 km/h
    return df_parsed


# --- Helper Function: haversine distance ---
# Symbols (符号): R: 地球平均半径; lat1, lon1, lat2, lon2: 两个点的经纬度。
# Units (单位): 距离为 km (公里)。
# Pronunciation (发音): Haversine /ˈhævərsaɪn/
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth's average radius in kilometers (地球平均半径，单位：公里)
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])  # 将角度转换为弧度

    dlon = lon2 - lon1  # 经度差
    dlat = lat2 - lat1  # 纬度差

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return distance


# --- New Helper Function: calculate_bearing (计算方位角) ---
# Symbols (符号): lat1, lon1, lat2, lon2: 两个点的经纬度。
# Units (单位): 方位角为度 (Degrees)，范围 0-360 度，0 度表示正北。
def calculate_bearing(lat1, lon1, lat2, lon2):
    """
    Calculates the initial bearing (direction) from point 1 to point 2.
    Returns bearing in degrees (0-360, where 0 is North).
    """
    if pd.isna(lat1) or pd.isna(lon1) or pd.isna(lat2) or pd.isna(lon2):
        return np.nan  # 如果任一坐标缺失，返回 NaN

    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])  # 将角度转换为弧度

    dlon = lon2 - lon1  # 经度差

    # 计算方位角的公式
    y = sin(dlon) * cos(lat2)
    x = cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(dlon)

    bearing = atan2(y, x)  # 计算弧度方位角
    bearing = degrees(bearing)  # 转换为度
    bearing = (bearing + 360) % 360  # 归一化到 0-360 度范围
    return bearing


# --- New Helper Function: categorize_direction (将方位角分类为基准方向) ---
# Analogy (比喻): 想象一个指南针的八个主要方向。
# Application (应用): 将连续的方位角数据离散化为更易分析和理解的类别。
def categorize_direction(bearing):
    if pd.isna(bearing):
        return np.nan
    # 逻辑 (Logic): 根据度数范围分配方向类别
    if 337.5 <= bearing < 360 or 0 <= bearing < 22.5:
        return 'N'  # 北
    elif 22.5 <= bearing < 67.5:
        return 'NE'  # 东北
    elif 67.5 <= bearing < 112.5:
        return 'E'  # 东
    elif 112.5 <= bearing < 157.5:
        return 'SE'  # 东南
    elif 157.5 <= bearing < 202.5:
        return 'S'  # 南
    elif 202.5 <= bearing < 247.5:
        return 'SW'  # 西南
    elif 247.5 <= bearing < 292.5:
        return 'W'  # 西
    elif 292.5 <= bearing < 337.5:
        return 'NW'  # 西北
    else:
        return np.nan  # 理论上不会发生，因为方位角已归一化


# --- Main execution logic for all steps ---
print("--- Step 2: Data Loading, Parsing and Initial Filtering ---")

# 正确的 GitHub 仓库路径结构
script_dir = os.path.dirname(os.path.abspath(__file__))  # 当前脚本所在目录 code/
project_root = os.path.dirname(script_dir)  # 回到项目根目录 TyphoonAnalysis_GitHub/

# 修正后的数据与输出路径
cma_data_dir = os.path.join(project_root, 'data', 'CMA')
output_dir = os.path.join(project_root, 'output')
csv_output_dir = os.path.join(output_dir, 'csv_sheet')

# 确保输出目录存在
os.makedirs(output_dir, exist_ok=True)
os.makedirs(csv_output_dir, exist_ok=True)

all_cma_tracks = []

if not os.path.exists(cma_data_dir):
    print(
        f"ERROR: Data directory '{cma_data_dir}' does not exist. Please ensure this directory is created and CMA data files are placed inside it."
    )
    df_cma_full = pd.DataFrame()
else:
    print(f"Searching for CMA data files in: '{cma_data_dir}'")
    found_files_in_dir = os.listdir(cma_data_dir)
    if not found_files_in_dir:
        print(f"Warning: Directory '{cma_data_dir}' is empty.")

    for filename in found_files_in_dir:
        if (
            filename.startswith('CH')
            and filename.endswith('BST.txt')
            and len(filename) == 13
            and filename[2:6].isdigit()
        ):  # CHYYYYBST.txt format
            year_in_filename = int(filename[2:6])

            if 1980 <= year_in_filename <= 2024:
                filepath = os.path.join(cma_data_dir, filename)
                df_single_year = parse_cma_track_file(filepath)
                if not df_single_year.empty:
                    all_cma_tracks.append(df_single_year)
                else:
                    print(f"      - No valid track data parsed from {filename}.")

    if all_cma_tracks:
        df_cma_full = pd.concat(all_cma_tracks).reset_index(drop=True)
        print(
            f"\nCMA complete dataset loaded. Total data entries: {len(df_cma_full)}"
        )
    else:
        print(
            f"\nERROR: No eligible CMA data files (CHXXXXBST.txt, 1980-2024) were found or successfully parsed in '{cma_data_dir}'."
        )
        df_cma_full = pd.DataFrame()

# Define the approximate boundaries for South China / East China region
min_lat_region = 15.0
max_lat_region = 40.0
min_lon_region = 105.0
max_lon_region = 130.0

if not df_cma_full.empty:
    df_region = df_cma_full[
        (df_cma_full['LAT'] >= min_lat_region)
        & (df_cma_full['LAT'] <= max_lat_region)
        & (df_cma_full['LON'] >= min_lon_region)
        & (df_cma_full['LON'] <= max_lon_region)
    ].copy()

    print(
        f"\nInitial filtering done. Number of typhoon events within wider South/East China region (Lat {min_lat_region}-{max_lat_region}N, Lon {min_lon_region}-{max_lon_region}E): {df_region['SID'].nunique()}"
    )

    # 修正后的 CSV 输出路径（保存到 output/csv_sheet/）
    df_region.to_csv(
        os.path.join(csv_output_dir, 'df_region_filtered.csv'), index=False
    )
    print(
        f"Saved df_region (initial filter) to {os.path.join(csv_output_dir, 'df_region_filtered.csv')}"
    )
else:
    print("\ndf_cma_full is empty, cannot proceed with regional filtering.")
    df_region = pd.DataFrame()


# --- Step 3: Identifying Typhoon Landfall Events and Landfall Points (Scheme B) ---
print("\n--- Step 3: Identifying Typhoon Landfall Events and Landfall Points (Scheme B) ---")

if not df_region.empty:
    # Define a stricter, approximate bounding box for mainland coastal China for landfall detection
    # This is a simplification and may include some large islands or miss complex coastlines.
    # Adjust these bounds based on your definition of "landfall" in South/East China.
    min_land_lat = 18.0  # Southernmost part of Guangdong/Guangxi coast (广东/广西海岸最南端)
    max_land_lat = 35.0  # Northern part of Jiangsu/Shandong coast (江苏/山东海岸最北端)
    min_land_lon = 108.0  # Western Guangxi coast (广西西部海岸)
    max_land_lon = 123.0  # Eastern Zhejiang/Shanghai coast (浙江东部/上海海岸)

    # Minimum intensity for a landfall event (Tropical Storm = Type Code 1 or above, Wind >= 63 km/h)
    min_landfall_type_code = 1
    min_landfall_wind_kmh = 63

    landfall_events = []

    for sid in df_region['SID'].unique():
        typhoon_track = (
            df_region[df_region['SID'] == sid]
            .sort_values(by='ISO_TIME')
            .reset_index(drop=True)
        )

        # Iterate through track points to find the first landfall
        for i in range(1, len(typhoon_track)):  # Start from the second point to compare with previous
            current_point = typhoon_track.iloc[i]
            previous_point = typhoon_track.iloc[i - 1]

            # Check if current point is over defined "land" and meets intensity criteria
            is_over_land = (
                (current_point['LAT'] >= min_land_lat)
                and (current_point['LAT'] <= max_land_lat)
                and (current_point['LON'] >= min_land_lon)
                and (current_point['LON'] <= max_land_lon)
            )

            is_strong_enough = (
                current_point['TYPE_CODE'] >= min_landfall_type_code
            ) and (current_point['WIND_KMH'] >= min_landfall_wind_kmh)

            # Check if previous point was NOT over "land" (i.e., over sea)
            was_over_sea_prev = not (
                (previous_point['LAT'] >= min_land_lat)
                and (previous_point['LAT'] <= max_land_lat)
                and (previous_point['LON'] >= min_land_lon)
                and (previous_point['LON'] <= max_land_lon)
            )

            # If current point is over land, strong enough, and previous was over sea -> potential landfall
            if is_over_land and is_strong_enough and was_over_sea_prev:
                # Record this point as landfall. Take the first one encountered.
                landfall_events.append(current_point.to_dict())
                break  # Move to next typhoon

    landfall_points_df = pd.DataFrame(landfall_events)

    if not landfall_points_df.empty:
        print(
            f"Identified {len(landfall_points_df)} potential landfall events (>= TS strength) using geospatial bounding box."
        )
        print("First 5 landfall points identified:")
        print(landfall_points_df.head())

        landfall_points_df.to_csv(
            os.path.join(csv_output_dir, 'df_landfall_points_schemeB.csv'),
            index=False,
        )
        print(
            f"Saved identified landfall points to {os.path.join(csv_output_dir, 'df_landfall_points_schemeB.csv')}"
        )
    else:
        print(
            "No landfall events identified using Scheme B. Please check bounding box and intensity criteria."
        )

    # Now, get pre-landfall 24-hour data using these identified landfall points
    def get_pre_landfall_data_schemeB(sid, landfall_time, df_full_track):
        track = (
            df_full_track[df_full_track['SID'] == sid]
            .sort_values(by='ISO_TIME')
            .reset_index(drop=True)
        )

        # Filter all data points within 24 hours BEFORE and including the landfall time
        start_time_window = landfall_time - pd.Timedelta(hours=24)
        data_24h_pre_landfall = track[
            (track['ISO_TIME'] >= start_time_window)
            & (track['ISO_TIME'] <= landfall_time)
        ].copy()

        if len(data_24h_pre_landfall) < 2:
            print(
                f"Warning: Typhoon {sid} has insufficient data points ({len(data_24h_pre_landfall)}) within 24 hours before landfall. Skipping."
            )
            return None
        return data_24h_pre_landfall

    all_pre_landfall_tracks = []
    if not landfall_points_df.empty:
        for index, row in landfall_points_df.iterrows():
            sid = row['SID']
            landfall_time = row['ISO_TIME']  # Get landfall time from the identified df

            pre_landfall_data = get_pre_landfall_data_schemeB(
                sid, landfall_time, df_region
            )
            if pre_landfall_data is not None:
                all_pre_landfall_tracks.append(pre_landfall_data)

    if all_pre_landfall_tracks:
        df_pre_landfall = pd.concat(all_pre_landfall_tracks).reset_index(drop=True)
        print(
            f"Successfully retrieved pre-landfall 24-hour data for {df_pre_landfall['SID'].nunique()} typhoons."
        )

        # 修正后的 CSV 输出路径（保存到 output/csv_sheet/）
        df_pre_landfall.to_csv(
            os.path.join(csv_output_dir, 'df_pre_landfall.csv'), index=False
        )
        print(
            f"Saved df_pre_landfall to {os.path.join(csv_output_dir, 'df_pre_landfall.csv')}"
        )
    else:
        print(
            "No sufficient pre-landfall 24-hour data for analysis after landfall identification. Check Step 3 logic."
        )
        df_pre_landfall = pd.DataFrame()

else:
    print("df_region is empty, cannot identify landfall events.")
    df_pre_landfall = pd.DataFrame()


# --- Step 4: Calculating Typhoon Movement Speed and Direction ---
print("\n--- Step 4: Calculating Typhoon Movement Speed and Direction ---")

if not df_pre_landfall.empty:
    df_pre_landfall = df_pre_landfall.sort_values(by=['SID', 'ISO_TIME']).reset_index(drop=True)

    # Calculate next point's lat/lon/time for each track point within each typhoon
    df_pre_landfall['next_lat'] = df_pre_landfall.groupby('SID')['LAT'].shift(-1)
    df_pre_landfall['next_lon'] = df_pre_landfall.groupby('SID')['LON'].shift(-1)
    df_pre_landfall['next_time'] = df_pre_landfall.groupby('SID')['ISO_TIME'].shift(-1)

    # Calculate distance (km) using Haversine formula
    df_pre_landfall['distance_km'] = df_pre_landfall.apply(
        lambda row: haversine(row['LAT'], row['LON'], row['next_lat'], row['next_lon'])
        if pd.notna(row['next_lat']) else None, axis=1
    )

    # Calculate time difference (hours)
    df_pre_landfall['time_diff_hours'] = (
        df_pre_landfall['next_time'] - df_pre_landfall['ISO_TIME']
    ).dt.total_seconds() / 3600

    # Calculate speed (km/h)
    df_pre_landfall['speed_kmh'] = df_pre_landfall['distance_km'] / df_pre_landfall['time_diff_hours']

    # NEW: Calculate bearing (方位角) and categorize direction (方向类别)
    df_pre_landfall['BEARING'] = df_pre_landfall.apply(
        lambda row: calculate_bearing(row['LAT'], row['LON'], row['next_lat'], row['next_lon'])
        if pd.notna(row['next_lat']) else np.nan, axis=1
    )
    df_pre_landfall['DIRECTION_CATEGORY'] = df_pre_landfall['BEARING'].apply(categorize_direction)

    avg_data_per_typhoon = []
    for sid in df_pre_landfall['SID'].unique():
        typhoon_data = df_pre_landfall[df_pre_landfall['SID'] == sid].copy()

        valid_speeds = typhoon_data['speed_kmh'].dropna()
        valid_directions = typhoon_data['DIRECTION_CATEGORY'].dropna()

        avg_speed = valid_speeds.mean() if not valid_speeds.empty else np.nan

        # Determine the most frequent direction
        dominant_direction = None
        if not valid_directions.empty:
            direction_counts = valid_directions.value_counts()
            if not direction_counts.empty:
                dominant_direction = direction_counts.idxmax()

        landfall_year = typhoon_data['YEAR'].iloc[-1]
        landfall_time = typhoon_data['ISO_TIME'].iloc[-1]

        avg_data_per_typhoon.append({
            'SID': sid,
            'YEAR': landfall_year,
            'Landfall_Time': landfall_time,
            'Avg_Speed_24h_kmh': avg_speed,
            'Dominant_Direction_24h': dominant_direction
        })

    df_avg_data_per_typhoon = pd.DataFrame(avg_data_per_typhoon)
    print(f"Calculated average pre-landfall 24-hour speeds and dominant directions for {len(df_avg_data_per_typhoon)} typhoons.")
    print("First 5 rows of df_avg_data_per_typhoon:")
    print(df_avg_data_per_typhoon.head())

    df_avg_data_per_typhoon.to_csv(os.path.join(csv_output_dir, 'df_avg_data_per_typhoon.csv'), index=False)
    print(f"Saved df_avg_data_per_typhoon to {os.path.join(csv_output_dir, 'df_avg_data_per_typhoon.csv')}")

else:
    print("df_pre_landfall is empty, cannot calculate typhoon movement speed or direction.")
    df_avg_data_per_typhoon = pd.DataFrame()



# --- Step 5: Trend Analysis and Visualization (Movement Speed) ---
print("\n--- Step 5: Trend Analysis and Visualization (Movement Speed) ---")

if not df_avg_data_per_typhoon.empty:
    df_analysis_speed = df_avg_data_per_typhoon.dropna(subset=['Avg_Speed_24h_kmh']).copy()

    plt.figure(figsize=(12, 7))
    sns.regplot(
        x='YEAR', y='Avg_Speed_24h_kmh', data=df_analysis_speed,
        scatter_kws={'alpha': 0.6, 'color': 'blue'},
        line_kws={'color': 'red', 'linestyle': '--'},
        ci=95
    )

    plt.title('Trend of Average Pre-landfall 24-hour Typhoon Translation Speed (1980-2024, CMA Data for South/East China Landfalls)', fontsize=16)
    plt.xlabel('Year', fontsize=14)
    plt.ylabel('Average Pre-landfall 24-hour Speed (km/h)', fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()

    plot_filepath_speed = os.path.join(output_dir, 'figures', '移速趋势_1980-2024.png')
    plt.savefig(plot_filepath_speed, dpi=300, bbox_inches='tight')
    print(f"Trend plot for speed saved to {plot_filepath_speed}")
    plt.show()

else:
    print("df_avg_data_per_typhoon is empty or has no valid speeds, cannot generate speed trend plot.")



# --- Step 5.1: Visualization of Movement Direction Distribution ---
print("\n--- Step 5.1: Visualization of Movement Direction Distribution ---")

if not df_avg_data_per_typhoon.empty:
    df_analysis_direction = df_avg_data_per_typhoon.dropna(subset=['Dominant_Direction_24h']).copy()

    if not df_analysis_direction.empty:
        direction_order = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
        df_analysis_direction['Dominant_Direction_24h'] = pd.Categorical(
            df_analysis_direction['Dominant_Direction_24h'],
            categories=direction_order,
            ordered=True
        )

        plt.figure(figsize=(10, 6))
        sns.countplot(
            x='Dominant_Direction_24h',
            data=df_analysis_direction,
            palette='viridis',
            order=direction_order
        )

        plt.title('Distribution of Dominant Pre-landfall 24-hour Typhoon Movement Directions (1980-2024, CMA Data)', fontsize=16)
        plt.xlabel('Dominant Movement Direction', fontsize=14)
        plt.ylabel('Number of Typhoon Events', fontsize=14)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()

        plot_filepath_direction = os.path.join(output_dir, 'figures', '方向分布_1980-2024.png')
        plt.savefig(plot_filepath_direction, dpi=300, bbox_inches='tight')
        print(f"Direction distribution plot saved to {plot_filepath_direction}")
        plt.show()

    else:
        print("No valid dominant directions for analysis, skipping direction distribution plot.")
else:
    print("df_avg_data_per_typhoon is empty, cannot generate direction distribution plot.")

# --- Step 6: Statistical Significance Testing (Movement Speed) ---
print("\n--- Step 6: Statistical Significance Testing (Movement Speed) ---")

df_analysis_speed = df_avg_data_per_typhoon.dropna(subset=['Avg_Speed_24h_kmh']).copy() \
    if not df_avg_data_per_typhoon.empty else pd.DataFrame()

if not df_analysis_speed.empty and len(df_analysis_speed) >= 2:
    slope, intercept, r_value, p_value, std_err = linregress(
        df_analysis_speed['YEAR'], df_analysis_speed['Avg_Speed_24h_kmh']
    )

    print("Linear Regression Results (Movement Speed):")
    print(f"Slope (Annual speed change): {slope:.3f} km/h/year")
    print(f"Intercept: {intercept:.3f} km/h")
    print(f"R-squared value: {r_value**2:.3f}")
    print(f"P-value: {p_value:.3f}")
    print(f"Standard Error: {std_err:.3f}")

    if p_value < 0.05:
        print("\nConclusion: The trend of average typhoon speed before landfall over years is statistically significant (p < 0.05).")
        if slope < 0:
            print("Specifically, the average speed before landfall shows a significant deceleration trend.")
        else:
            print("Specifically, the average speed before landfall shows a significant acceleration trend.")
    else:
        print("\nConclusion: The trend of average typhoon speed before landfall over years is not statistically significant (p >= 0.05).")

else:
    print("Not enough data to perform linear regression analysis for speed (at least 2 typhoon data points are required).")
    slope = None
    p_value = None
    r_value = None


# --- Step 7: Preliminary Interpretation of Results and Discussion Points ---
print("\n--- Step 7: Preliminary Interpretation of Results and Discussion Points ---")

print("Based on the results from Step 5, 5.1 and Step 6, you can now start drafting your 'Results' section.")
print("Example wording for your 'Results' section:")
print(f"    对1980-2024年间CMA提供的共计 {df_avg_data_per_typhoon['SID'].nunique()} 个登陆华南/华东地区的台风最佳路径数据进行分析。")

# Speed results (移速结果)
if not df_analysis_speed.empty and slope is not None:
    if p_value < 0.05:
        trend_direction_speed = "减慢" if slope < 0 else "加快"
        print(
            f"    结果显示，在登陆前24小时的平均移动速度随年份变化呈现显著的{trend_direction_speed}趋势"
            f"（线性回归p值 = {p_value:.3f}，R² = {r_value**2:.3f}），"
            f"平均速度以每年 {abs(slope):.3f} km/h/年的速度{trend_direction_speed}。"
            f"这一发现与H1（速度）中提出的台风在登陆前减慢（Stalling）的假设 "
            f"[如果 slope < 0 则为一致，否则为不一致]。"
        )
    else:
        print(
            f"    统计分析（线性回归p值 = {p_value:.3f}）表明，台风登陆前平均速度随年份变化的趋势不具有统计显著性。"
            "这意味着在1980-2024年间，中国华南/华东登陆台风在登陆前24小时的平均移动速度没有观测到显著的长期变化。"
        )
else:
    print("    由于速度数据不足，无法得出关于速度趋势的统计结论。")

print("    图1（即你Step 5生成的速度趋势图像）展示了各年度登陆台风的平均速度及趋势线。")


# Direction results (方向结果)
# 确保 df_analysis_direction 已定义（来自 Step 5.1）
if 'df_analysis_direction' in globals() and not df_analysis_direction.empty:
    most_common_direction = df_analysis_direction['Dominant_Direction_24h'].mode()[0]
    print(
        f"    在台风移动方向方面，登陆前24小时主导方向频次分布显示，最常见的移动方向是 {most_common_direction} 方向。"
        "这表明在该区域，台风在登陆前倾向于沿此方向移动。"
    )
    print("    图2（即你Step 5.1生成的方向分布图像）展示了主导移动方向的频次分布。")
else:
    print("    由于方向数据不足，无法得出关于移动方向的结论。")


print("\nConsider the following points for your 'Discussion' section:")
print("1. **验证假设 (移速)**: 你的移速结果是支持还是反对了台风登陆前减慢的假设？为什么？即使不显著，也需要讨论这与全球趋势的异同和可能原因。")
print("2. **趋势原因 (移速，如果显著)**: 探讨观测到的速度变化（减慢/加快）可能的气候学原因，例如副热带高压、行星波、海洋热含量等。")
print("3. **趋势原因 (移速，如果不显著)**: 探讨为什么没有观测到显著移速趋势，可能是区域差异、数据精度、采样频率等因素。")
print("4. **移动方向特征**: 分析主导移动方向的分布是否与已有认识一致，是否存在年代际变化趋势。")
print("5. **移速与方向的关联**: 探讨是否某些方向更容易出现“Stalling”现象。")
print("6. **方法论局限性**: 边界框法识别登陆点的局限性，可能误判台湾/海南登陆为大陆登陆。")
print("7. **数据质量**: CMA 早期数据质量较低，可能影响趋势分析。")
print("8. **与现有研究对比**: 与 Kossin (2014), Hall & Kossin (2019) 等研究进行对比，讨论一致性与差异。")
print("9. **未来工作**: 可加入海岸线 shapefile、区域分组、强度分组、环境变量回归、路径聚类等进一步分析。")

print("\n--- All steps completed. Review the output in your VS Code terminal and 'output' folder. ---")
