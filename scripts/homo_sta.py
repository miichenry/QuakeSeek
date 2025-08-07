import pandas as pd
from sklearn.metrics.pairwise import euclidean_distances
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.transforms import offset_copy
import pandas as pd
import sys
import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import os
import seaborn

def select_homogeneous_stations(input_csv_path, output_csv_path, num_stations_to_select=20):
    """
    Loads station data from a CSV, selects a specified number of stations
    with a relatively homogeneous spatial distribution, and saves them to a new CSV.

    Args:
        input_csv_path (str): Path to the input CSV file.
                               Must contain 'latitude' and 'longitude' columns.
        output_csv_path (str): Path to save the output CSV file.
        num_stations_to_select (int): The number of stations to select.
    """
    try:
        # Load the station data
        df = pd.read_csv(input_csv_path, dtype={'station':str})
    except FileNotFoundError:
        print(f"Error: Input file not found at {input_csv_path}")
        return
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return

    if not all(col in df.columns for col in ['latitude', 'longitude']):
        print("Error: CSV must contain 'latitude' and 'longitude' columns.")
        return

    if len(df) < num_stations_to_select:
        print(f"Error: Input CSV has only {len(df)} stations. "
              f"Cannot select {num_stations_to_select} stations.")
        return

    # Extract coordinates
    coordinates = df[['latitude', 'longitude']].values

    selected_indices = []
    selected_coordinates_list = []

    if len(df) == num_stations_to_select:
        # If the number of stations is exactly what we need, select all
        selected_df = df.copy()
    elif num_stations_to_select > 0 :
        # 1. Randomly select the first station
        first_station_index = np.random.choice(len(df))
        selected_indices.append(first_station_index)
        selected_coordinates_list.append(coordinates[first_station_index])

        # 2. Iteratively select the remaining stations
        for _ in range(1, num_stations_to_select):
            min_distances_to_selected = []
            for i in range(len(coordinates)):
                if i not in selected_indices:
                    point_coord = coordinates[i].reshape(1, -1)
                    # Calculate distances from the current point to all already selected points
                    distances = euclidean_distances(point_coord, np.array(selected_coordinates_list))
                    # Find the minimum distance to any of the selected points
                    min_distances_to_selected.append(np.min(distances))
                else:
                    # Already selected or not a candidate, assign a very small distance
                    min_distances_to_selected.append(-1) # Ensures it won't be chosen

            # Select the point that has the maximum minimum_distance to any selected point
            next_station_index = np.argmax(min_distances_to_selected)
            selected_indices.append(next_station_index)
            selected_coordinates_list.append(coordinates[next_station_index])

        selected_df = df.iloc[selected_indices]
    else: # num_stations_to_select is 0 or negative
        selected_df = pd.DataFrame(columns=df.columns)


    # Save the selected stations to a new CSV
    try:
        selected_df.to_csv(output_csv_path, index=False)
        print(f"Successfully selected {len(selected_df)} stations and saved to {output_csv_path}")
    except Exception as e:
        print(f"Error saving CSV: {e}")

input_file = '/home/users/h/henrymi/jectpro/sibual/stations_sibualbuali.csv'
output_file = './stations_4_detection.csv'
select_homogeneous_stations(input_file, output_file, num_stations_to_select=63)

