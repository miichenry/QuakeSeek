import numpy as np
import json
import matplotlib.pyplot as plt
from glob import glob
from obspy import UTCDateTime, read
import pandas as pd

project = 'LUCERNE'
path_data = '/home/users/h/henrymi/qseek_lu/v3/my-search'.format(project)
json_file = path_data + '/detections_receivers.json'
json_file_eq = '/home/users/h/henrymi/qseek_lu/v3/my-search/csv/detections.csv'
path_mseed = '/srv/beegfs/scratch/users/h/henrymi/lu_mseed_small'
freqmin = 1.0
freqmax = 10.0

df = pd.read_csv(json_file_eq)
eq_n_stations = df['n_stations']
eq_latitude = df['lat']
eq_longitude = df['lon']

# Open and read the JSON file
with open(json_file, 'r') as file:

    for line in file:
        data = json.loads(line)
        print(data)
        n_receivers = data['n_receivers']
        print(n_receivers)
        print(eq_n_stations[0])

        event_id = data['event_uid']
        receivers = data['receivers']
        k = 0
        fig = plt.figure(figsize=(10, 10))
        station_names = []
        station_names_ixs = []

        for receiver in receivers:
            
            # --- FIX STARTS HERE ---
            # Safely get phase arrival data using .get() to avoid errors
            phase_arrivals = receiver.get('phase_arrivals')
            station = receiver.get('station')

            # Check if essential data exists
            if not station or not phase_arrivals:
                print(f"Skipping receiver due to missing station name or phase data.")
                continue

            p_arrival = phase_arrivals.get('cake:P')
            s_arrival = phase_arrivals.get('cake:S')

            # Check if BOTH P and S arrivals exist before proceeding
            if not p_arrival or not s_arrival:
                print(f"Skipping station {station} because it is missing a P or S pick.")
                continue
            # --- FIX ENDS HERE ---

            try:
                # Now it's safe to access the nested data
                P_picking_time = UTCDateTime(p_arrival['observed']['time'])
                S_picking_time = UTCDateTime(s_arrival['observed']['time'])

                stations_files = sorted(glob(path_mseed + '/SS.{:s}.SW.DPZ.*.{:d}.{:02d}.{:02d}.*.Z.miniseed'.format(station,
                                                                                                                   P_picking_time.year,
                                                                                                                   P_picking_time.month,
                                                                                                                   P_picking_time.day )))

                if len(stations_files) == 0:
                    continue
                else:
                    st = read(stations_files[0])
                    st[0].detrend('demean')
                    st[0].trim(starttime=P_picking_time-5, endtime=P_picking_time+10)
                    st[0].filter("bandpass", freqmin=freqmin, freqmax=freqmax, corners=4, zerophase=True)

                    tr = st[0]
                    # Start time of the trace
                    start_time = tr.stats.starttime
                    absolute_times = tr.times("utcdatetime")
                    signal_data = tr.data*10
                    signal_data += k
                    plt.plot(absolute_times, signal_data, 'k-')
                    plt.vlines(x=P_picking_time, ymin=np.min(signal_data), ymax=np.max(signal_data), colors='red')
                    plt.vlines(x=S_picking_time, ymin=np.min(signal_data), ymax=np.max(signal_data), colors='blue')
                    station_names.append(station)
                    station_names_ixs.append(k)
                    k +=1
            except Exception as e:
                # This will catch any other unexpected errors during processing
                print(f'Error processing station {station}: {e}')

        plt.yticks(station_names_ixs, station_names)
        plt.savefig(f'/home/users/h/henrymi/qseek_lu/v3/{event_id}.png', dpi=500)
        #plt.show()
        plt.close(fig)


