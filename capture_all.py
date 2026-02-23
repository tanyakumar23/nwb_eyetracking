'''
This file extracts saccades and fixations (along with metadata) for each patient per task phase.
Encoding vs Recognition are taken from the trials table (not filename). Events are split by phase
(fully inside encoding or recognition window). Blink-overlapping events are marked as artifacts.
Saves to pkl/flagged_eye_events.pkl with structure: [pid][R1|R2][Encoding|Recognition] = list of events.
-> metadata for saccade: amplitude, velocity, duration, startX, startY, endX, endY, pupil_vel
-> Same event format as sac_fix: type ('Saccade'/'Fixation' as in NWB), duration, amplitude, velocity, pupil_size; 
capture_all also adds is_artifact.
start,end can be added if neeeded 
'''
import os
import pickle
import numpy as np
from pynwb import NWBHDF5IO

current_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(current_dir, 'nwb files')
output_folder = os.path.join(current_dir, 'pkl')

def get_event_list_with_metadata(beh_module, name):
    """Extracts events and maps the specific columns per event type."""
    if name not in beh_module.data_interfaces:
        return []
    
    ts = beh_module[name]['TimeSeries']
    timestamps = ts.timestamps[:]
    data = ts.data[:]
    
    events = []
    for i in range(len(timestamps)):
        start_t = float(timestamps[i])
        
        event_dict = {'start': start_t}
        
        if name == 'Saccade':
            dur = float(data[i][0])
            event_dict.update({
                'type': 'Saccade',
                'end': start_t + dur,
                'duration': dur,
                'amplitude': float(data[i][5]),
                'velocity': float(data[i][6])
            })
            
        elif name == 'Fixation':
            dur = float(data[i][0])
            event_dict.update({
                'type': 'Fixation',
                'end': start_t + dur,
                'duration': dur,
                'pupil_size': float(data[i][3])
            })
            
        elif name == 'Blink':
            dur = float(data[i])
            event_dict.update({
                'end': start_t + dur,
                'duration': dur
            })

        events.append(event_dict)
    return events


def get_encoding_recognition_windows(nwb):
    """Encoding/recognition windows from trials (sorted by start_time: row 0 = encoding, rest = recognition)."""
    trials = nwb.intervals['trials']
    starts = np.asarray(trials['start_time'].data[:])
    stops = np.asarray(trials['stop_time'].data[:])
    order = np.argsort(starts)
    starts, stops = starts[order], stops[order]
    enco_start, enco_stop = float(starts[0]), float(stops[0])
    reco_start, reco_stop = float(starts[1]), float(stops[-1])
    return (enco_start, enco_stop), (reco_start, reco_stop)


def split_events_by_phase(events, enco_window, reco_window):
    """Events fully inside encoding or recognition only. Each event must have 'start' and 'end'."""
    enco_start, enco_stop = enco_window
    reco_start, reco_stop = reco_window
    encoding_events = []
    recognition_events = []
    for ev in events:
        s, e = ev['start'], ev['end']
        if enco_start <= s and e <= enco_stop:
            encoding_events.append(ev)
        elif reco_start <= s and e <= reco_stop:
            recognition_events.append(ev)
    return encoding_events, recognition_events


# Storage for results
full_data_results = {}

print("Marking artifacts (blink-overlaps) and splitting by Encoding/Recognition from trials...\n")

for root, _, files in os.walk(data_path):
    for f_name in files:
        if not f_name.endswith('.nwb'):
            continue
        pid = f_name.split('_')[0]
        run_key = 'R1' if 'CSR1' in f_name else 'R2'
        run_label = '(R1)' if run_key == 'R1' else '(R2)'
        full_path = os.path.join(root, f_name)
        try:
            with NWBHDF5IO(full_path, 'r') as io:
                nwb = io.read()
                beh = nwb.processing['behavior']

                enco_window, reco_window = get_encoding_recognition_windows(nwb)
                blinks = get_event_list_with_metadata(beh, 'Blink')
                saccades = get_event_list_with_metadata(beh, 'Saccade')
                fixations = get_event_list_with_metadata(beh, 'Fixation')

                # Mark blink-overlap artifacts (blink start/end first in condition)
                for s in saccades:
                    s['is_artifact'] = any((b['start'] < s['end']) and (b['end'] > s['start']) for b in blinks)
                for f in fixations:
                    f['is_artifact'] = any((b['start'] < f['end']) and (b['end'] > f['start']) for b in blinks)

                # Split by phase: only events fully inside encoding or recognition
                enc_saccades, rec_saccades = split_events_by_phase(saccades, enco_window, reco_window)
                enc_fixations, rec_fixations = split_events_by_phase(fixations, enco_window, reco_window)

                enc_sequence = enc_saccades + enc_fixations
                rec_sequence = rec_saccades + rec_fixations
                enc_sequence.sort(key=lambda x: x['start'])
                rec_sequence.sort(key=lambda x: x['start'])

                if pid not in full_data_results:
                    full_data_results[pid] = {}
                if run_key not in full_data_results[pid]:
                    full_data_results[pid][run_key] = {}
                full_data_results[pid][run_key]['Encoding'] = enc_sequence
                full_data_results[pid][run_key]['Recognition'] = rec_sequence

                enc_art = sum(1 for e in enc_sequence if e['is_artifact'])
                rec_art = sum(1 for e in rec_sequence if e['is_artifact'])
                print(f"{pid} {run_label}: Encoding {len(enc_sequence)} events ({enc_art} artifacts), Recognition {len(rec_sequence)} events ({rec_art} artifacts).")
        except Exception as e:
            print(f"Error in {f_name}: {e}")

# Save
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

save_path = os.path.join(output_folder, 'flagged_eye_events.pkl')
with open(save_path, 'wb') as f:
    pickle.dump(full_data_results, f)

print(f"\nFlagged data saved to: {save_path}")