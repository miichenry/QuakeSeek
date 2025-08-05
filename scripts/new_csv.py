import pandas as pd
import random

# Load the CSV file
input_csv = 'station.csv'  # Replace with your CSV file path
df = pd.read_csv(input_csv)

# Check if there are at least 20 rows
if len(df) < 20:
    raise ValueError("The CSV file contains fewer than 20 rows.")

# Randomly select 20 rows
df_sampled = df.sample(n=20, random_state=42)  # `random_state` ensures reproducibility

# Save the sampled data to a new CSV file
output_csv = 'sampled_20_stations.csv'
df_sampled.to_csv(output_csv, index=False)

print(f"Sampled 20 rows saved to {output_csv}")

