import pandas as pd
import shutil
import glob
import os

# Settings
input_csv = 'stations_4_detection.csv'                   # Path to your input CSV
source_dir = '/srv/beegfs/scratch/users/h/henrymi/sibual_mseed_renamed'      # Directory containing the files (with subdirectories)
output_dir = '/srv/beegfs/scratch/users/h/henrymi/sibual_data/sibual_QuakeSeek_mseed'              # Destination directory for copied files

# Create the output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Load CSV and sample 20 rows
df = pd.read_csv(input_csv, dtype={'station':str})

#if len(df) < 20:
#    raise ValueError("The CSV file contains fewer than 20 rows.")

#sampled_df = df.sample(n=20, random_state=42)
#sampled_df.to_csv('sampled_20_rows.csv', index=False)

# Get the unique station values
station_values = df['station'].unique()

# Copy matching files from all subdirectories
for station in station_values:
    print(station)
    pattern = os.path.join(source_dir, '**', f'SS.{station}.*')
    matching_files = glob.glob(pattern, recursive=True)
    
    for file_path in matching_files:
        shutil.copy(file_path, output_dir)

print(f"Copied files for sampled stations to '{output_dir}'")

