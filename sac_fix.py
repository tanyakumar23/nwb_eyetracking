''' This files extracts the saccades and fixations for each patient per task,
 encoding and recognition. The logic is start time+duration = end time'''
import os
import pickle
from pynwb import NWBHDF5IO

# Paths
data_path = r'E:\eyetracking\nwb files'
output_folder = r'C:\Users\Tanya\bmovie-release-NWB-BIDS\code\codebase'

# exclude 44, 58, 60 (only 1 run) and 53 (calibration issues)
excluded_patients = ['sub-CS44', 'sub-CS53', 'sub-CS58', 'sub-CS60']

def get_event_timeline(beh_module):
    timeline = []
    
    # Extract Saccades using column [0] for duration
    if 'Saccade' in beh_module.data_interfaces:
        sac_ts = beh_module['Saccade']['TimeSeries']
        for i, start_t in enumerate(sac_ts.timestamps):
            dur = sac_ts.data[i][0]
            timeline.append({
                'event': 'saccade', 
                'start': start_t, 
                'end': start_t + dur
            })
            
    # Extract Fixations using column [0] for duration
    if 'Fixation' in beh_module.data_interfaces:
        fix_ts = beh_module['Fixation']['TimeSeries']
        for i, start_t in enumerate(fix_ts.timestamps):
            dur = fix_ts.data[i][0]
            timeline.append({
                'event': 'fixation', 
                'start': start_t, 
                'end': start_t + dur
            })
    
    # Sort to ensure the end of one matches the start of the next
    timeline.sort(key=lambda x: x['start'])
    return timeline

master_dict = {}
files_processed = 0

print(f"Starting extraction from {data_path}...")

for root, dirs, files in os.walk(data_path):
    for f_name in files:
        if f_name.endswith('.nwb'):
            pid = f_name.split('_')[0]
            
            # Run for everyone EXCEPT the excluded list
            if pid not in excluded_patients:
                full_path = os.path.join(root, f_name)
                try:
                    with NWBHDF5IO(full_path, 'r') as io:
                        nwb = io.read()
                        beh = nwb.processing['behavior']
                        
                        if pid not in master_dict:
                            master_dict[pid] = {'Encoding': [], 'Recognition': []}
                        
                        # CSR1 is Encoding, CSR2 is Recognition
                        session_key = 'Encoding' if 'CSR1' in f_name else 'Recognition'
                        master_dict[pid][session_key] = get_event_timeline(beh)
                        files_processed += 1
                        print(f"Successfully processed: {f_name}")
                        
                except Exception as e:
                    print(f"Error in {f_name}: {e}")

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

output_path = os.path.join(output_folder, 'isolated_eye_events.pkl')
with open(output_path, 'wb') as f:
    pickle.dump(master_dict, f)

print("\n--- EXTRACTION COMPLETE ---")
print(f"Total Files processed: {files_processed}")

print(f"Total Patients in dict: {len(master_dict)}")
