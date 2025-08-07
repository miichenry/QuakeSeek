import obspy
from obspy.core.inventory import Inventory
import pandas as pd

df = pd.read_csv('stations_4_detection.csv')
stations_to_keep_codes  = df['station'].astype(str).tolist()
print(stations_to_keep_codes)

input_xml_file = "/home/users/h/henrymi/jectpro/sibual/sibualbuali_stations_nodes.xml"  # <--- CHANGE THIS
output_xml_file = "/home/users/h/henrymi/QuakeSeek/sarulla1/stations_4_detection.xml" # <--- CHANGE THIS (output file name)

print(f"Attempting to load inventory from: {input_xml_file}")
try:
    # Load the full inventory from your StationXML file
    inv = obspy.read_inventory(input_xml_file, format="STATIONXML")
except Exception as e:
    print(f"Error loading XML file '{input_xml_file}': {e}")
    print("Please ensure the file path is correct and the file is a valid StationXML.")
    exit()

print(f"Successfully loaded {len(inv.networks)} network(s) with a total of {len(inv.get_contents()['stations'])} station(s).")

# Create a new inventory object to store the filtered and modified stations
filtered_inv = Inventory(
    networks=[],
    source=inv.source  # Preserve the source information from the original file
)

stations_found_and_processed = 0
# Use a dictionary to reconstruct networks to avoid duplicates if stations from the same network are processed
networks_in_filtered_inv = {} 

for net_original in inv:
    for sta_original in net_original:
        if sta_original.code in stations_to_keep_codes:
            # Ensure network exists in the filtered inventory
            if net_original.code not in networks_in_filtered_inv:
                new_net = net_original.copy() # Copy network structure
                new_net.stations = []         # Clear its stations list to add only filtered ones
                networks_in_filtered_inv[net_original.code] = new_net
                filtered_inv.networks.append(new_net)
            else:
                new_net = networks_in_filtered_inv[net_original.code]

            # Copy the station to avoid modifying the original inventory object in memory
            sta_modified = sta_original.copy()

            print(f"Processing station: {net_original.code}.{sta_modified.code}")
            
            # --- Modify Station-level elevation ---
            if sta_modified.elevation is not None:
                original_station_elevation_m = sta_modified.elevation
                # Convert the numerical elevation value to represent kilometers
                new_station_elevation_value_for_km = original_station_elevation_m / 1000.0
                sta_modified.elevation = new_station_elevation_value_for_km 
                
                print(f"  Station-level original elevation: {original_station_elevation_m} M")
                print(f"  Station-level new numerical elevation value: {sta_modified.elevation} (intended to represent km)")
            else:
                print(f"  Station {net_original.code}.{sta_modified.code} has no station-level elevation data.")

            # --- Modify Channel-level elevation for all channels in this station ---
            print(f"  Checking channel-level elevations for {len(sta_modified.channels)} channel(s):")
            for chan in sta_modified.channels: # Iterate through channels of the copied station
                if chan.elevation is not None:
                    original_channel_elevation_m = chan.elevation
                    # Convert the numerical channel elevation value
                    new_channel_elevation_value_for_km = original_channel_elevation_m / 1000.0
                    chan.elevation = new_channel_elevation_value_for_km 
                    
                    print(f"    Channel {chan.code}: Original elevation: {original_channel_elevation_m} M -> New value: {chan.elevation}")
                else:
                    print(f"    Channel {chan.code}: No channel-level elevation data.")
            
            new_net.stations.append(sta_modified)
            stations_found_and_processed += 1

if stations_found_and_processed > 0:
    print(f"\nFinished processing. Kept and modified {stations_found_and_processed} station(s).")
    print(f"Saving modified inventory to: {output_xml_file}")
    try:
        # Write the new inventory to an XML file.
        # ObsPy will write the new numerical elevation values for both station and channel.
        # The 'unit' attribute for elevation will still be "M" (meters)
        # as per StationXML standard and ObsPy's behavior.
        filtered_inv.write(output_xml_file, format="STATIONXML", validate=True)
        print(f"Successfully saved '{output_xml_file}'.")
        print("\n--- IMPORTANT NOTE ON THE OUTPUT FILE ---")
        print("The <Elevation> values for the selected stations AND THEIR CHANNELS in the output XML")
        print("file have been numerically divided by 1000 (to represent kilometer values).")
        print("However, ObsPy, by default and adhering to StationXML standards, will")
        print("still write the attribute `unit=\"M\"` next to these new numerical values")
        print("for both station and channel elevations.")
        print("If you intend for a downstream tool to interpret these new smaller numbers")
        print("as kilometer values (possibly ignoring or overriding the 'M' unit attribute),")
        print("this output may suit your needs for specific workarounds.")
        print("If you strictly require the attribute to be `unit=\"KILOMETERS\"`, you would")
        print("need to manually edit the output XML file with a text editor or use more")
        print("advanced XML parsing tools, as this is not standard StationXML for elevation.")
        print("---")

    except Exception as e:
        print(f"Error writing output XML file '{output_xml_file}': {e}")
else:
    print("\nNo stations matching the provided codes were found in the input file. No output file written.")
