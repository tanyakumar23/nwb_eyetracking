''' Extracts saccades and fixations per patient, split by Encoding vs Recognition using
    the trials table (not filename). Logic: start_time + duration = end_time for each event;
    events are assigned to Encoding or Recognition based on whether they fall inside the
    encoding or recognition time window from trials. '''
import os
import pickle
import numpy as np
from pynwb import NWBHDF5IO

# Paths: folder containing sub-CS*/ subfolders with .nwb files
data_path = r'e:\eyetracking\nwb files'
output_folder = r'e:\eyetracking\pkl'


def get_encoding_recognition_windows(nwb):
    """Get (enco_start, enco_stop) and (reco_start, reco_stop) from trials table.
    Trials are sorted by start_time; row 0 is always the one encoding trial, rest are recognition."""
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


def get_event_timeline(beh_module):
    """Build list of saccade/fixation events with start and end times. duration = data[i][0]."""
    timeline = []
    # Saccades: col 0=duration, 5=amplitude, 6=velocity (pupil_vel)
    if 'Saccade' in beh_module.data_interfaces:
        sac_ts = beh_module['Saccade']['TimeSeries']
        timestamps = np.asarray(sac_ts.timestamps[:])
        data = np.asarray(sac_ts.data[:])
        for i in range(len(timestamps)):
            start_t = float(timestamps[i])
            dur = float(data[i, 0])
            timeline.append({
                'type': 'Saccade',
                'start': start_t,
                'end': start_t + dur,
                'duration': dur,
                'amplitude': float(data[i, 5]),
                'velocity': float(data[i, 6])
            })
    # Fixations: col 0=duration, 3=pupil_avg (pupil size)
    if 'Fixation' in beh_module.data_interfaces:
        fix_ts = beh_module['Fixation']['TimeSeries']
        timestamps = np.asarray(fix_ts.timestamps[:])
        data = np.asarray(fix_ts.data[:])
        for i in range(len(timestamps)):
            start_t = float(timestamps[i])
            dur = float(data[i, 0])
            timeline.append({
                'type': 'Fixation',
                'start': start_t,
                'end': start_t + dur,
                'duration': dur,
                'pupil_size': float(data[i, 3])
            })
    timeline.sort(key=lambda x: x['start'])
    return timeline


def split_events_by_phase(timeline, enco_window, reco_window):
    """Keep only events that are fully inside encoding or fully inside recognition (both start and end in the same phase)."""
    enco_start, enco_stop = enco_window
    reco_start, reco_stop = reco_window
    encoding_events = []
    recognition_events = []
    for event in timeline:
        start_time = event['start']
        end_time = event['end']
        if enco_start <= start_time and end_time <= enco_stop:
            encoding_events.append(event)
        elif reco_start <= start_time and end_time <= reco_stop:
            recognition_events.append(event)
    return encoding_events, recognition_events


master_dict = {}
files_processed = 0

print(f"Starting extraction from {data_path}...")

for root, _, files in os.walk(data_path):
    for f_name in files:
        if not f_name.endswith('.nwb'):
            continue
        pid = f_name.split('_')[0]
        run_label = '(R1)' if 'CSR1' in f_name else '(R2)'
        full_path = os.path.join(root, f_name)
        try:
            with NWBHDF5IO(full_path, 'r') as io:
                nwb = io.read()
                beh = nwb.processing['behavior']
                enco_window, reco_window = get_encoding_recognition_windows(nwb)
                timeline = get_event_timeline(beh)
                encoding_events, recognition_events = split_events_by_phase(timeline, enco_window, reco_window)
            if pid not in master_dict:
                master_dict[pid] = {
                    'R1': {'Encoding': [], 'Recognition': []},
                    'R2': {'Encoding': [], 'Recognition': []}
                }
            run_key = 'R1' if 'CSR1' in f_name else 'R2'
            master_dict[pid][run_key]['Encoding'].extend(encoding_events)
            master_dict[pid][run_key]['Recognition'].extend(recognition_events)
            files_processed += 1
            print(f"  {pid} {run_label}: Encoding={len(encoding_events)}, Recognition={len(recognition_events)}")
        except Exception as e:
            print(f"Error in {f_name}: {e}")

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

output_path = os.path.join(output_folder, 'isolated_eye_events.pkl')
with open(output_path, 'wb') as f:
    pickle.dump(master_dict, f)

print("\nEXTRACTION COMPLETE")
print(f"Total files processed: {files_processed}")
print(f"Patients in dict: {len(master_dict)}")
