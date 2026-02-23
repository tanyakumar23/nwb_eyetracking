'''Counts blinks per patient split by Encoding vs Recognition using the trials table.
   Only blinks fully inside encoding or fully inside recognition are counted (same rule as saccades/fixations).'''
import os
import numpy as np
from pynwb import NWBHDF5IO

data_path = r'e:\eyetracking\nwb files'


def get_encoding_recognition_windows(nwb):
    """Trials sorted by start_time; row 0 = encoding, rest = recognition."""
    trials = nwb.intervals['trials']
    starts = np.asarray(trials['start_time'].data[:])
    stops = np.asarray(trials['stop_time'].data[:])
    order = np.argsort(starts)
    starts = starts[order]
    stops = stops[order]
    enco_start = float(starts[0])
    enco_stop = float(stops[0])
    reco_start = float(starts[1])
    reco_stop = float(stops[-1])
    return (enco_start, enco_stop), (reco_start, reco_stop)


print(f"{'Patient':<18} | {'Encoding':<10} | {'Recognition':<12}")
print("-" * 45)

for root, _, files in os.walk(data_path):
    for f_name in files:
        if not f_name.endswith('.nwb'):
            continue
        pid = f_name.split('_')[0]
        run_label = '(R1)' if 'CSR1' in f_name else '(R2)'
        pid_display = f"{pid} {run_label}"
        full_path = os.path.join(root, f_name)
        try:
            with NWBHDF5IO(full_path, 'r') as io:
                nwb = io.read()
                beh = nwb.processing['behavior']
                enco_window, reco_window = get_encoding_recognition_windows(nwb)
                enco_start, enco_stop = enco_window
                reco_start, reco_stop = reco_window

                if 'Blink' not in beh.data_interfaces:
                    print(f"{pid_display:<18} | {'0':<10} | {'0':<12}")
                    continue

                blink_ts = beh['Blink']['TimeSeries']
                timestamps = np.asarray(blink_ts.timestamps[:])
                durations = np.asarray(blink_ts.data[:])

                encoding_count = 0
                recognition_count = 0
                for i in range(len(timestamps)):
                    start_time = float(timestamps[i])
                    dur = float(durations[i]) if durations.size > i else 0.0
                    end_time = start_time + dur
                    if enco_start <= start_time and end_time <= enco_stop:
                        encoding_count += 1
                    elif reco_start <= start_time and end_time <= reco_stop:
                        recognition_count += 1

                print(f"{pid_display:<18} | {encoding_count:<10} | {recognition_count:<12}")

        except Exception as e:
            print(f"Error reading {f_name}: {e}")


print("Blink count complete.")
