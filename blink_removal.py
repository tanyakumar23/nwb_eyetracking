''' Categorizes blinks into isolated vs contamination-causing and counts contaminated
    saccades/fixations (for each patient per run R1/R2). Prints results only; no pkl saved. '''
import os
import numpy as np
from pynwb import NWBHDF5IO

data_path = r'e:\eyetracking\nwb files'


def get_event_list(beh_module, name):
    """Extract events with start/end; column 0 = duration for movements, 1D for blinks."""
    if name not in beh_module.data_interfaces:
        return []

    ts = beh_module[name]['TimeSeries']
    timestamps = np.asarray(ts.timestamps[:])
    data = np.asarray(ts.data[:])

    events = []
    for i in range(len(timestamps)):
        start_t = float(timestamps[i])
        if name == 'Blink':
            dur = float(np.ravel(data)[i])
        else:
            dur = float(data[i, 0])
        events.append({'start': start_t, 'end': start_t + dur})
    return events


print("Categorizing Blinks and Counting Contaminated Events...\n")

for root, _, files in os.walk(data_path):
    for f_name in files:
        if not f_name.endswith('.nwb'):
            continue
        pid = f_name.split('_')[0]
        run_key = 'R1' if 'CSR1' in f_name else 'R2'
        run_label = '(R1)' if 'CSR1' in f_name else '(R2)'
        full_path = os.path.join(root, f_name)
        try:
            with NWBHDF5IO(full_path, 'r') as io:
                nwb = io.read()
                beh = nwb.processing['behavior']

                blinks = get_event_list(beh, 'Blink')
                saccades = get_event_list(beh, 'Saccade')
                fixations = get_event_list(beh, 'Fixation')
                movements = saccades + fixations

            isolated_blinks = []
            contamination_blinks = []
            contaminated_event_count = 0

            for b in blinks:
                is_contaminator = False
                for m in movements:
                    if (b['start'] < m['end']) and (b['end'] > m['start']):
                        is_contaminator = True
                        break
                if is_contaminator:
                    contamination_blinks.append(b)
                else:
                    isolated_blinks.append(b)

            for m in movements:
                for b in blinks:
                    if (b['start'] < m['end']) and (b['end'] > m['start']):
                        contaminated_event_count += 1
                        break

            print(f"{pid} {run_label}: {len(isolated_blinks)} isolated, {len(contamination_blinks)} contamination blinks, {contaminated_event_count} contaminated events")

        except Exception as e:
            print(f"Error in {f_name}: {e}")
