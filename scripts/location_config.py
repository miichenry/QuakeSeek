import pandas as pd
import math
import io
import json

# Provided base configuration from your request
base_config = {
    "location": {
        "lat": 47.056051751257165,
        "lon": 8.304790003581305,
        "east_shift": 0.0,
        "north_shift": 0.0,
        "elevation": 0.0,
        "depth": 0.0
    },
    "root_node_size": 1000.0, # This is the critical value for the octree
    "n_levels": 5,
    "east_bounds": [
        -10000.0,
        10000.0
    ],
    "north_bounds": [
        -10000.0,
        10000.0
    ],
    "depth_bounds": [
        0.0,
        20000.0
    ]
    }
# Define your CSV file name
station_csv = '../sarulla1/stations_4_detection.csv'

# Define the maximum depth for the depth_bounds.
# This value is fixed and should be a multiple of root_node_size if it defines the total depth extent.
# In your base_config, 20000.0 is already a multiple of 1000.0 (20000 / 1000 = 20).
fixed_max_depth = 20000.0

# --- Function to convert Latitude/Longitude difference to meters ---
def latlon_to_meters(lat_ref, lon_ref, lat_point, lon_point):
    """
    Calculates approximate east and north shifts in meters from a reference point.

    Args:
        lat_ref (float): Reference latitude (decimal degrees).
        lon_ref (float): Reference longitude (decimal degrees).
        lat_point (float): Point latitude (decimal degrees).
        lon_point (float): Point longitude (decimal degrees).

    Returns:
        tuple: (east_shift_meters, north_shift_meters)
    """
    R = 6371000.0 # Earth's mean radius in meters

    lat_ref_rad = math.radians(lat_ref)
    lon_ref_rad = math.radians(lon_ref)
    lat_point_rad = math.radians(lat_point)
    lon_point_rad = math.radians(lon_point)

    delta_lat = lat_point_rad - lat_ref_rad
    delta_lon = lon_point_rad - lon_ref_rad

    north_shift_meters = delta_lat * R
    east_shift_meters = delta_lon * R * math.cos(lat_ref_rad)

    return east_shift_meters, north_shift_meters

# --- Load the CSV data ---
try:
    df = pd.read_csv(station_csv)
except FileNotFoundError:
    print(f"Error: CSV file '{station_csv}' not found. Please ensure the file exists in the correct directory.")
    exit()
except KeyError as e:
    print(f"Error: Missing expected column in CSV. Please ensure 'latitude', 'longitude', and 'depth' columns exist. Details: {e}")
    exit()
except Exception as e:
    print(f"An unexpected error occurred while loading or processing CSV: {e}")
    exit()

# --- Calculate the geographical center (lat/lon) of the station cluster ---
# This center will be the new reference point for the local coordinate system.
center_lat = (df['latitude'].min() + df['latitude'].max()) / 2.0
center_lon = (df['longitude'].min() + df['longitude'].max()) / 2.0

print(f"Calculated Geographical Center Latitude: {center_lat}")
print(f"Calculated Geographical Center Longitude: {center_lon}")

# --- Calculate east_shift and north_shift for each station relative to the calculated center ---
df['east_shift_meters'] = 0.0
df['north_shift_meters'] = 0.0

for index, row in df.iterrows():
    east_m, north_m = latlon_to_meters(center_lat, center_lon, row['latitude'], row['longitude'])
    df.at[index, 'east_shift_meters'] = east_m
    df.at[index, 'north_shift_meters'] = north_m

# --- Determine the min/max shifts from the station data ---
min_east_data = df['east_shift_meters'].min()
max_east_data = df['east_shift_meters'].max()
min_north_data = df['north_shift_meters'].min()
max_north_data = df['north_shift_meters'].max()

# The depth values from the CSV are not directly used to calculate depth_bounds span
# as you've provided a fixed 'depth' variable and base_config depth_bounds.
# However, if you wanted to calculate depth bounds from station data, you'd use:
# min_depth_data = df['depth'].min()
# max_depth_data = df['depth'].max()

# --- Get root_node_size from the base_config ---
root_node_size = base_config["root_node_size"]

# --- Define conservative buffer ---
CONSERVATIVE_BUFFER_METERS = 500.0 # Add 500 meters buffer on each side

# --- Calculate the required total span for east and north, including the buffer ---
# Ensure the span is a multiple of root_node_size for octree compatibility.
initial_span_east = (max_east_data - min_east_data) + 2 * CONSERVATIVE_BUFFER_METERS
adjusted_east_span = math.ceil(initial_span_east / root_node_size) * root_node_size

initial_span_north = (max_north_data - min_north_data) + 2 * CONSERVATIVE_BUFFER_METERS
adjusted_north_span = math.ceil(initial_span_north / root_node_size) * root_node_size

# --- Calculate the midpoints of the station data ranges ---
midpoint_east_data = (min_east_data + max_east_data) / 2.0
midpoint_north_data = (min_north_data + max_north_data) / 2.0

# --- Construct the new east and north bounds ---
# These bounds are centered on the station data's midpoint but span the adjusted_X_span.
new_east_bounds = [midpoint_east_data - adjusted_east_span / 2.0, midpoint_east_data + adjusted_east_span / 2.0]
new_north_bounds = [midpoint_north_data - adjusted_north_span / 2.0, midpoint_north_data + adjusted_north_span / 2.0]

# --- Set depth_bounds ---
# Using the fixed_max_depth and ensuring the lower bound is 0.0.
# The total depth (fixed_max_depth - 0.0) should already be a multiple of root_node_size.
new_depth_bounds = [0.0, fixed_max_depth]

# --- Update the base_config with calculated values ---
updated_config = base_config.copy()

# Update the 'location' lat/lon to be the calculated center of the station network.
updated_config["location"]["lat"] = center_lat
updated_config["location"]["lon"] = center_lon

# The 'east_shift' and 'north_shift' in 'location' are 0.0 because the local coordinate
# system's origin is now defined by the 'location' lat/lon (the center of the stations).
updated_config["location"]["east_shift"] = 0.0
updated_config["location"]["north_shift"] = 0.0
# The 'depth' in 'location' can be set to the average depth of stations if needed,
# or kept as 0.0 if it refers to the surface. For now, keeping it as 0.0 as per original.
updated_config["location"]["depth"] = 0.0 # Or (df['depth'].min() + df['depth'].max()) / 2.0 if you want center depth

# Update the east, north, and depth bounds with the newly calculated conservative and
# octree-compatible bounds.
updated_config["east_bounds"] = new_east_bounds
updated_config["north_bounds"] = new_north_bounds
updated_config["depth_bounds"] = new_depth_bounds

# Print the updated configuration in a nicely formatted JSON output
print("\n--- Updated Configuration ---")
print(json.dumps(updated_config, indent=4))
