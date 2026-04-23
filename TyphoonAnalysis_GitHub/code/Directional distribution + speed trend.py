import pandas as pd
import os
from math import radians, sin, cos, sqrt, atan2, degrees
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import linregress
import numpy as np  # Needed for numerical operations, e.g., handling NaN values


# ---------------------------------------------------------
# Matplotlib font settings (Chinese fonts kept for compatibility)
# ---------------------------------------------------------
# Note: Windows 11 may not include Chinese fonts by default.
# If missing, Chinese characters in plots may appear as boxes.
# You may install fonts or replace with available system fonts.
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False  # Ensures minus signs display correctly


# ---------------------------------------------------------
# Helper Function: parse_cma_track_file (robust parsing)
# ---------------------------------------------------------
def parse_cma_track_file(filepath):
    data = []
    current_typhoon_sid = None
    current_typhoon_name = None

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:  # Skip empty lines
                continue

            # Identify typhoon header lines (contain typhoon ID and name)
            # Example: 66666 0000 14 0001 8301 0 6 Sarah 20110729
            if line.startswith('66666'):
                parts = line.split()
                if len(parts) >= 8:
                    typhoon_id_code_str = parts[4]  # e.g., '8301', '2401'
                    typhoon_year_prefix = typhoon_id_code_str[:2]
                    typhoon_num_suffix = typhoon_id_code_str[2:]

                    full_year = int(typhoon_year_prefix)
                    if 80 <= full_year <= 99:      # 1980–1999
                        full_year_str = f"19{typhoon_year_prefix}"
                    elif 0 <= full_year <= 24:     # 2000–2024
                        full_year_str = f"20{typhoon_year_prefix}"
                    else:
                        print(
                            f"Warning: Unrecognized year prefix {typhoon_year_prefix} "
                            f"in typhoon ID {typhoon_id_code_str} from file {filepath}. "
                            f"Using XXXX as year."
                        )
                        full_year_str = "XXXX"

                    current_typhoon_sid = f"{full_year_str}{typhoon_num_suffix.zfill(2)}"
                    current_typhoon_name = parts[7]  # e.g., 'Sarah', 'EWINIAR'
                else:
                    print(
                        f"Warning: Header line in {filepath} has fewer than 8 parts: '{line}'. Skipping."
                    )
                    current_typhoon_sid = None
                    current_typhoon_name = None
                    continue

            # Process track data lines
            # Example: 1983062300 0 140 1170 1004 10
            elif current_typhoon_sid:
                parts = line.split()
                if len(parts) >= 6:
                    try:
                        datetime_str = parts[0]  # YYYYMMDDHH
                        year = int(datetime_str[:4])
                        month = int(datetime_str[4:6])
                        day = int(datetime_str[6:8])
                        hour = int(datetime_str[8:10])
                        iso_time = pd.to_datetime(
                            f"{year}-{month:02d}-{day:02d} {hour:02d}:00:00"
                        )

                        type_code = int(parts[1])
                        lat = float(parts[2]) / 10.0
                        lon = float(parts[3]) / 10.0
                        pressure = int(parts[4])
                        wind_ms = float(parts[5])

                        data.append([
                            current_typhoon_sid,
                            current_typhoon_name,
                            iso_time,
                            type_code,
                            lat,
                            lon,
                            pressure,
                            wind_ms
                        ])
                    except (ValueError, IndexError) as e:
                        print(
                            f"Failed to parse track line (SID: {current_typhoon_sid}, line: '{line}'), error: {e}"
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
            'SID', 'NAME', 'ISO_TIME', 'TYPE_CODE',
            'LAT', 'LON', 'PRESSURE', 'WIND_MS'
        ]
    )
    df_parsed['YEAR'] = df_parsed['ISO_TIME'].dt.year
    df_parsed['WIND_KMH'] = df_parsed['WIND_MS'] * 3.6  # Convert m/s → km/h
    return df_parsed


# ---------------------------------------------------------
# Helper Function: Haversine distance (km)
# ---------------------------------------------------------
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius (km)
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


# ---------------------------------------------------------
# Helper Function: Calculate bearing (0–360°, 0° = North)
# ---------------------------------------------------------
def calculate_bearing(lat1, lon1, lat2, lon2):
    if pd.isna(lat1) or pd.isna(lon1) or pd.isna(lat2) or pd.isna(lon2):
        return np.nan

    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1

    y = sin(dlon) * cos(lat2)
    x = cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(dlon)

    bearing = atan2(y, x)
    bearing = degrees(bearing)
    return (bearing + 360) % 360


# ---------------------------------------------------------
# Helper Function: Categorize bearing into compass directions
# ---------------------------------------------------------
def categorize_direction(bearing):
    if pd.isna(bearing):
        return np.nan

    if 337.5 <= bearing < 360 or 0 <= bearing < 22.5:
        return 'N'
    elif 22.5 <= bearing < 67.5:
        return 'NE'
    elif 67.5 <= bearing < 112.5:
        return 'E'
    elif 112.5 <= bearing < 157.5:
        return 'SE'
    elif 157.5 <= bearing < 202.5:
        return 'S'
    elif 202.5 <= bearing < 247.5:
        return 'SW'
    elif 247.5 <= bearing < 292.5:
        return 'W'
    elif 292.5 <= bearing < 337.5:
        return 'NW'
    else:
        return np.nan


# ---------------------------------------------------------
# Step 2: Data Loading, Parsing and Initial Filtering
# ---------------------------------------------------------
print("--- Step 2: Data Loading, Parsing and Initial Filtering ---")

script_dir = os.path.dirname(os.path.abspath(__file__))  # /code/
project_root = os.path.dirname(script_dir)               # /TyphoonAnalysis_GitHub/

cma_data_dir = os.path.join(project_root, 'data', 'CMA')
output_dir = os.path.join(project_root, 'output')
csv_output_dir = os.path.join(output_dir, 'csv_sheet')

os.makedirs(output_dir, exist_ok=True)
os.makedirs(csv_output_dir, exist_ok=True)

all_cma_tracks = []

if not os.path.exists(cma_data_dir):
    print(f"ERROR: Data directory '{cma_data_dir}' does not exist. Please add CMA files.")
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
        ):
            year_in_filename = int(filename[2:6])

            if 1980 <= year_in_filename <= 2024:
                filepath = os.path.join(cma_data_dir, filename)
                df_single_year = parse_cma_track_file(filepath)

                if not df_single_year.empty:
                    all_cma_tracks.append(df_single_year)
                else:
                    print(f"  - No valid track data parsed from {filename}.")

    if all_cma_tracks:
        df_cma_full = pd.concat(all_cma_tracks).reset_index(drop=True)
        print(f"\nCMA complete dataset loaded. Total entries: {len(df_cma_full)}")
    else:
        print("\nERROR: No valid CMA files found or parsed.")
        df_cma_full = pd.DataFrame()


# ---------------------------------------------------------
# Regional filtering (South/East China bounding box)
# ---------------------------------------------------------
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
        f"\nInitial filtering complete. Number of typhoon events in South/East China region: "
        f"{df_region['SID'].nunique()}"
    )

    df_region.to_csv(
        os.path.join(csv_output_dir, 'df_region_filtered.csv'),
        index=False
    )
    print(f"Saved df_region to {os.path.join(csv_output_dir, 'df_region_filtered.csv')}")
else:
    print("\ndf_cma_full is empty. Cannot proceed with regional filtering.")
    df_region = pd.DataFrame()



# --- Step 3: Identifying Typhoon Landfall Events and Landfall Points (Scheme B) ---
print("\n--- Step 3: Identifying Typhoon Landfall Events and Landfall Points (Scheme B) ---")

if not df_region.empty:
    # Define a stricter bounding box for mainland coastal China for landfall detection.
    # This is a simplified approximation and may include some large islands or miss complex coastlines.
    # Adjust these bounds based on your definition of “landfall” in South/East China.
    min_land_lat = 18.0   # Southernmost part of Guangdong/Guangxi coast
    max_land_lat = 35.0   # Northern Jiangsu/Shandong coast
    min_land_lon = 108.0  # Western Guangxi coast
    max_land_lon = 123.0  # Eastern Zhejiang/Shanghai coast

    # Minimum intensity for a landfall event (Tropical Storm = Type Code ≥ 1, Wind ≥ 63 km/h)
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
        for i in range(1, len(typhoon_track)):  # Start from second point
            current_point = typhoon_track.iloc[i]
            previous_point = typhoon_track.iloc[i - 1]

            # Check if current point is over land and meets intensity criteria
            is_over_land = (
                (current_point['LAT'] >= min_land_lat)
                and (current_point['LAT'] <= max_land_lat)
                and (current_point['LON'] >= min_land_lon)
                and (current_point['LON'] <= max_land_lon)
            )

            is_strong_enough = (
                current_point['TYPE_CODE'] >= min_landfall_type_code
                and current_point['WIND_KMH'] >= min_landfall_wind_kmh
            )

            # Check if previous point was over sea
            was_over_sea_prev = not (
                (previous_point['LAT'] >= min_land_lat)
                and (previous_point['LAT'] <= max_land_lat)
                and (previous_point['LON'] >= min_land_lon)
                and (previous_point['LON'] <= max_land_lon)
            )

            # If current point is over land, strong enough, and previous was over sea → landfall
            if is_over_land and is_strong_enough and was_over_sea_prev:
                landfall_events.append(current_point.to_dict())
                break  # Move to next typhoon

    landfall_points_df = pd.DataFrame(landfall_events)

    if not landfall_points_df.empty:
        print(f"Identified {len(landfall_points_df)} potential landfall events (>= TS strength).")
        print("First 5 landfall points:")
        print(landfall_points_df.head())

        landfall_points_df.to_csv(
            os.path.join(csv_output_dir, 'df_landfall_points_schemeB.csv'),
            index=False
        )
        print(f"Saved landfall points to {os.path.join(csv_output_dir, 'df_landfall_points_schemeB.csv')}")
    else:
        print("No landfall events identified using Scheme B. Check bounding box and intensity criteria.")

    # Function to extract 24-hour pre-landfall data
    def get_pre_landfall_data_schemeB(sid, landfall_time, df_full_track):
        track = (
            df_full_track[df_full_track['SID'] == sid]
            .sort_values(by='ISO_TIME')
            .reset_index(drop=True)
        )

        start_time_window = landfall_time - pd.Timedelta(hours=24)
        data_24h_pre_landfall = track[
            (track['ISO_TIME'] >= start_time_window)
            & (track['ISO_TIME'] <= landfall_time)
        ].copy()

        if len(data_24h_pre_landfall) < 2:
            print(
                f"Warning: Typhoon {sid} has insufficient data points "
                f"({len(data_24h_pre_landfall)}) within 24 hours before landfall. Skipping."
            )
            return None
        return data_24h_pre_landfall

    # Collect pre-landfall tracks
    all_pre_landfall_tracks = []
    if not landfall_points_df.empty:
        for index, row in landfall_points_df.iterrows():
            sid = row['SID']
            landfall_time = row['ISO_TIME']

            pre_landfall_data = get_pre_landfall_data_schemeB(sid, landfall_time, df_region)
            if pre_landfall_data is not None:
                all_pre_landfall_tracks.append(pre_landfall_data)

    if all_pre_landfall_tracks:
        df_pre_landfall = pd.concat(all_pre_landfall_tracks).reset_index(drop=True)
        print(f"Retrieved 24-hour pre-landfall data for {df_pre_landfall['SID'].nunique()} typhoons.")

        df_pre_landfall.to_csv(
            os.path.join(csv_output_dir, 'df_pre_landfall.csv'),
            index=False
        )
        print(f"Saved df_pre_landfall to {os.path.join(csv_output_dir, 'df_pre_landfall.csv')}")
    else:
        print("No sufficient pre-landfall data available. Check Step 3 logic.")
        df_pre_landfall = pd.DataFrame()

else:
    print("df_region is empty. Cannot identify landfall events.")
    df_pre_landfall = pd.DataFrame()


# --- Step 4: Calculating Typhoon Movement Speed and Direction ---
print("\n--- Step 4: Calculating Typhoon Movement Speed and Direction ---")

if not df_pre_landfall.empty:
    df_pre_landfall = df_pre_landfall.sort_values(by=['SID', 'ISO_TIME']).reset_index(drop=True)

    # Compute next-point coordinates and time
    df_pre_landfall['next_lat'] = df_pre_landfall.groupby('SID')['LAT'].shift(-1)
    df_pre_landfall['next_lon'] = df_pre_landfall.groupby('SID')['LON'].shift(-1)
    df_pre_landfall['next_time'] = df_pre_landfall.groupby('SID')['ISO_TIME'].shift(-1)

    # Distance (km)
    df_pre_landfall['distance_km'] = df_pre_landfall.apply(
        lambda row: haversine(row['LAT'], row['LON'], row['next_lat'], row['next_lon'])
        if pd.notna(row['next_lat']) else None,
        axis=1
    )

    # Time difference (hours)
    df_pre_landfall['time_diff_hours'] = (
        df_pre_landfall['next_time'] - df_pre_landfall['ISO_TIME']
    ).dt.total_seconds() / 3600

    # Speed (km/h)
    df_pre_landfall['speed_kmh'] = df_pre_landfall['distance_km'] / df_pre_landfall['time_diff_hours']

    # Bearing and direction category
    df_pre_landfall['BEARING'] = df_pre_landfall.apply(
        lambda row: calculate_bearing(row['LAT'], row['LON'], row['next_lat'], row['next_lon'])
        if pd.notna(row['next_lat']) else np.nan,
        axis=1
    )
    df_pre_landfall['DIRECTION_CATEGORY'] = df_pre_landfall['BEARING'].apply(categorize_direction)

    # Compute average speed and dominant direction per typhoon
    avg_data_per_typhoon = []
    for sid in df_pre_landfall['SID'].unique():
        typhoon_data = df_pre_landfall[df_pre_landfall['SID'] == sid].copy()

        valid_speeds = typhoon_data['speed_kmh'].dropna()
        valid_directions = typhoon_data['DIRECTION_CATEGORY'].dropna()

        avg_speed = valid_speeds.mean() if not valid_speeds.empty else np.nan

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
    print("First 5 rows:")
    print(df_avg_data_per_typhoon.head())

    df_avg_data_per_typhoon.to_csv(
        os.path.join(csv_output_dir, 'df_avg_data_per_typhoon.csv'),
        index=False
    )
    print(f"Saved df_avg_data_per_typhoon to {os.path.join(csv_output_dir, 'df_avg_data_per_typhoon.csv')}")

else:
    print("df_pre_landfall is empty. Cannot calculate movement speed or direction.")
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

    plt.title('Trend of Average Pre-landfall 24-hour Typhoon Translation Speed (1980–2024, CMA Data for South/East China Landfalls)', fontsize=16)
    plt.xlabel('Year', fontsize=14)
    plt.ylabel('Average Pre-landfall 24-hour Speed (km/h)', fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()

    plot_filepath_speed = os.path.join(output_dir, 'figures', 'speed_trend_1980_2024.png')
    plt.savefig(plot_filepath_speed, dpi=300, bbox_inches='tight')
    print(f"Speed trend plot saved to: {plot_filepath_speed}")
    plt.show()

else:
    print("df_avg_data_per_typhoon is empty or contains no valid speed data. Cannot generate speed trend plot.")



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

        plt.title('Distribution of Dominant Pre-landfall 24-hour Typhoon Movement Directions (1980–2024, CMA Data)', fontsize=16)
        plt.xlabel('Dominant Movement Direction', fontsize=14)
        plt.ylabel('Number of Typhoon Events', fontsize=14)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()

        plot_filepath_direction = os.path.join(output_dir, 'figures', 'direction_distribution_1980_2024.png')
        plt.savefig(plot_filepath_direction, dpi=300, bbox_inches='tight')
        print(f"Direction distribution plot saved to: {plot_filepath_direction}")
        plt.show()

    else:
        print("No valid dominant direction data available. Skipping direction distribution plot.")
else:
    print("df_avg_data_per_typhoon is empty. Cannot generate direction distribution plot.")



# --- Step 6: Statistical Significance Testing (Movement Speed) ---
print("\n--- Step 6: Statistical Significance Testing (Movement Speed) ---")

df_analysis_speed = df_avg_data_per_typhoon.dropna(subset=['Avg_Speed_24h_kmh']).copy() \
    if not df_avg_data_per_typhoon.empty else pd.DataFrame()

if not df_analysis_speed.empty and len(df_analysis_speed) >= 2:
    slope, intercept, r_value, p_value, std_err = linregress(
        df_analysis_speed['YEAR'], df_analysis_speed['Avg_Speed_24h_kmh']
    )

    print("Linear Regression Results (Movement Speed):")
    print(f"Slope (annual speed change): {slope:.3f} km/h/year")
    print(f"Intercept: {intercept:.3f} km/h")
    print(f"R-squared value: {r_value**2:.3f}")
    print(f"P-value: {p_value:.3f}")
    print(f"Standard error: {std_err:.3f}")

    if p_value < 0.05:
        print("\nConclusion: The trend in average pre-landfall typhoon speed is statistically significant (p < 0.05).")
        if slope < 0:
            print("Specifically, typhoons show a significant deceleration trend before landfall.")
        else:
            print("Specifically, typhoons show a significant acceleration trend before landfall.")
    else:
        print("\nConclusion: No statistically significant trend in pre-landfall typhoon speed (p ≥ 0.05).")

else:
    print("Not enough data for linear regression (minimum 2 typhoons required).")
    slope = None
    p_value = None
    r_value = None



# --- Step 7: Preliminary Interpretation of Results and Discussion Points ---
print("\n--- Step 7: Preliminary Interpretation of Results and Discussion Points ---")

print("Based on the results from Step 5, Step 5.1, and Step 6, you can now begin drafting your 'Results' section.")
print("Example wording for your 'Results' section:")
print(f"    A total of {df_avg_data_per_typhoon['SID'].nunique()} landfalling typhoons affecting South/East China from 1980–2024 were analyzed using CMA best-track data.")

# Speed results
if not df_analysis_speed.empty and slope is not None:
    if p_value < 0.05:
        trend_direction_speed = "decrease" if slope < 0 else "increase"
        print(
            f"    Results show a statistically significant {trend_direction_speed} in average pre-landfall "
            f"24-hour translation speed over time (p = {p_value:.3f}, R² = {r_value**2:.3f}). "
            f"The mean speed changes at a rate of {abs(slope):.3f} km/h per year. "
            f"This finding is {'' if slope < 0 else 'not '}consistent with the hypothesis (H1) "
            f"that typhoons slow down (stall) before landfall."
        )
    else:
        print(
            f"    Statistical analysis (p = {p_value:.3f}) indicates no significant long-term trend in "
            f"pre-landfall typhoon translation speed from 1980–2024."
        )
else:
    print("    Insufficient speed data to draw conclusions about long-term speed trends.")

print("    Figure 1 (generated in Step 5) shows the annual average pre-landfall speed and its regression trend line.")


# Direction results
if 'df_analysis_direction' in globals() and not df_analysis_direction.empty:
    most_common_direction = df_analysis_direction['Dominant_Direction_24h'].mode()[0]
    print(
        f"    Regarding movement direction, the most common dominant direction during the 24 hours before landfall "
        f"is {most_common_direction}. This suggests a preferred approach direction for landfalling typhoons in this region."
    )
    print("    Figure 2 (generated in Step 5.1) shows the distribution of dominant movement directions.")
else:
    print("    Insufficient direction data to draw conclusions about movement direction characteristics.")


print("\nConsider the following points for your 'Discussion' section:")
print("1. **Hypothesis evaluation (speed):** Does your result support or contradict the hypothesis that typhoons slow down before landfall?")
print("2. **Possible causes (if significant):** Discuss potential climatic drivers such as subtropical high variability, steering flow changes, or ocean thermal structure.")
print("3. **Possible causes (if not significant):** Consider regional differences, data limitations, or compensating environmental factors.")
print("4. **Movement direction characteristics:** Are the dominant directions consistent with known climatology? Any interdecadal shifts?")
print("5. **Speed–direction relationship:** Are certain approach directions associated with slower-moving (stalling) typhoons?")
print("6. **Methodological limitations:** Bounding-box landfall detection may misclassify Taiwan/Hainan landfalls as mainland landfalls.")
print("7. **Data quality:** Early CMA data may have lower accuracy, affecting trend detection.")
print("8. **Comparison with existing studies:** Compare with Kossin (2014), Hall & Kossin (2019), and other global translation-speed studies.")
print("9. **Future work:** Consider coastline shapefiles, regional subgrouping, intensity stratification, environmental regressions, or track clustering.")

print("\n--- All steps completed. Review the output in your VS Code terminal and 'output' folder. ---")
