'''Converts the pickle of flagged eye events to a table for viewing. Uses standard format: type, duration, amplitude, 
velocity, pupil_size, is_artifact. start,end can be added if neeeded '''
import pickle
import os
import pandas as pd

current_dir = os.path.dirname(os.path.abspath(__file__))
pkl_folder = os.path.join(current_dir, 'pkl')
pkl_path = os.path.join(pkl_folder, 'flagged_eye_events.pkl')

with open(pkl_path, 'rb') as f:
    master_dict = pickle.load(f)

# Pick patient and run (R1/R2) and phase (Encoding/Recognition)
pid, run, phase = 'sub-CS41', 'R1', 'Encoding'
if pid not in master_dict or run not in master_dict[pid]:
    print(f"{pid} {run} not in pickle.")
else:
    data_list = master_dict[pid][run][phase]
    df = pd.DataFrame(data_list)

    # Column order: standard keys only (no x, y, startX, etc.)
    cols = ['type', 'start', 'end', 'duration', 'amplitude', 'velocity', 'pupil_size', 'is_artifact']
    cols = [c for c in cols if c in df.columns]
    df = df[cols]

    print(f"Table: {pid} {run} {phase} (first 10 rows):")
    print(df.head(10))

    if 'is_artifact' in df.columns and df['is_artifact'].any():
        print("\nArtifacts (blink-overlap):")
        print(df[df['is_artifact'] == True])
    else:
        print("\nNo artifacts in this slice.")

    # Optional: save to CSV
    # df.to_csv(os.path.join(pkl_folder, f'{pid}_{run}_{phase}.csv'), index=False)
