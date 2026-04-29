import os
import pandas as pd

# Get script directory and construct correct CSV path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)

# Correct CSV path (consistent with your repository structure)
csv_path = os.path.join(project_root, 'output', 'csv_sheet', 'df_avg_data_per_typhoon.csv')

df = pd.read_csv(csv_path)

# Count frequency of dominant movement directions
direction_counts = df['Dominant_Direction_24h'].value_counts()
print("Frequency distribution of dominant movement directions:")
print(direction_counts)

# Calculate percentages
direction_percent = df['Dominant_Direction_24h'].value_counts(normalize=True) * 100
print("\nPercentage distribution of dominant movement directions:")
print(direction_percent)

# Display in a specific order (e.g., N, NE, E, SE, S, SW, W, NW)
ordered_categories = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
direction_counts_ordered = df['Dominant_Direction_24h'].value_counts().reindex(ordered_categories)
print("\nFrequency distribution in directional order:")
print(direction_counts_ordered)

