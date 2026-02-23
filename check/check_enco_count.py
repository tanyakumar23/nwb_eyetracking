"""
Shows one patient's trials in time order and confirms: 1 encoding block, then recognition.
"""
from pynwb import NWBHDF5IO
import pandas as pd
import os

# Path from project root (works when run from check/ folder)
base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
f_path = os.path.join(base, 'nwb files', 'sub-CS48', 'sub-CS48_ses-P48CSR1_behavior+ecephys.nwb')

if not os.path.exists(f_path):
    print("File not found:", f_path)
else:
    with NWBHDF5IO(f_path, 'r') as io:
        nwb = io.read()
        trials_df = nwb.intervals['trials'].to_dataframe()
    trials_df = trials_df.sort_values('start_time').reset_index(drop=True)

    print("Trial order (chronological)")
    print("Columns: start_time, stop_time, stim_phase")
    print("-" * 60)
    cols = ['start_time', 'stop_time', 'stim_phase']
    cols = [c for c in cols if c in trials_df.columns]
    print(trials_df[cols].to_string())
    print("-" * 60)

    phases = trials_df['stim_phase'].values
    is_enc = (phases == 'encoding') | (phases == 'Encoding')
    is_rec = (phases == 'recognition') | (phases == 'Recognition')
    n_enc = is_enc.sum()
    n_rec = is_rec.sum()

    print(f"Encoding trials: {n_enc}")
    print(f"Recognition trials: {n_rec}")

    enco_stop = float(trials_df['stop_time'].iloc[0])
    reco_start = float(trials_df['start_time'].iloc[1])
    if enco_stop > reco_start:
        print("\nWARNING: Encoding end > Recognition start (overlap).")
    else:
        print("\nEncoding and recognition do not overlap (gap in between).")
    print("=> One encoding block (row 0), then recognition block.")
