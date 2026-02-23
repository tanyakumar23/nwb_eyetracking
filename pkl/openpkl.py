'''
Opens the pickle file and prints a preview plus summary per patient and run (R1 / R2).
'''
import pickle
import os

pkl_folder = r'e:\eyetracking\pkl'
pkl_path = os.path.join(pkl_folder, 'flagged_eye_events.pkl')

with open(pkl_path, 'rb') as f:
    master_dict = pickle.load(f)

# Preview: first 5 events (type = Saccade/Fixation as in NWB dataset; flagged pkl also has is_artifact)
preview_pid = 'sub-CS41'
preview_run = 'R1'
if preview_pid in master_dict and preview_run in master_dict[preview_pid]:
    preview = master_dict[preview_pid][preview_run]['Encoding'][:5]
    print(f"Preview: {preview_pid} {preview_run} Encoding (first 5 events):")
    for event in preview:
        t = event['type']
        line = f"  {t} | Start: {event['start']:.3f} | End: {event['end']:.3f} | Duration: {event['duration']:.3f}"
        if t == 'Saccade':
            line += f" | Amplitude: {event['amplitude']:.3f} | Velocity: {event['velocity']:.3f}"
        elif t == 'Fixation':
            line += f" | Pupil size: {event['pupil_size']:.3f}"
        if 'is_artifact' in event:
            line += f" | artifact={event['is_artifact']}"
        print(line)
else:
    print(f"Preview: {preview_pid} / {preview_run} not in pickle.")

# Summary: per patient, per run
print("\nSummary")
for pid in sorted(master_dict.keys()):
    runs = master_dict[pid]
    for run in ['R1', 'R2']:
        if run not in runs:
            continue
        enc_count = len(runs[run]['Encoding'])
        rec_count = len(runs[run]['Recognition'])
        print(f"{pid} ({run}): Encoding={enc_count}, Recognition={rec_count}")
