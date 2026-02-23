"""
Simple view of the trials table: see start_time, stop_time, stim_phase. It shows the encoding and recognition phase start and stop times.
 There is only 1 encoding row because it was continuous 1 task. there are 40 recognition rows because they had 40 frames for yes or no answers.
This table shows there are no rows during the gap (time between encoding end and recognition start) but there is a gap.
"""
from pynwb import NWBHDF5IO
import pandas as pd
import os

f_path = r'e:\eyetracking\nwb files\sub-CS43\sub-CS43_ses-P43CSR2_behavior+ecephys.nwb'

if not os.path.exists(f_path):
    print("File not found:", f_path)
else:
    with NWBHDF5IO(f_path, 'r') as io:
        nwb = io.read()
        trials_df = nwb.intervals['trials'].to_dataframe()

    trials_df = trials_df.sort_values('start_time').reset_index(drop=True)

    # Show the columns you care about
    cols = ['start_time', 'stop_time', 'stim_phase']
    # Keep only column names that actually exist in the table
    new_cols = []
    for c in cols:
        if c in trials_df.columns:
            new_cols.append(c)
    df = trials_df[new_cols]

    print("TRIALS (sorted by start_time)")
    print("Each row = one trial. Gap = time when there are NO rows.\n")
    print(df.to_string())
    print("\n---")
    print("Encoding ends at stop_time of last encoding row.")
    print("Recognition starts at start_time of first recognition row.")
    print("Between those two times there are NO rows — that's the gap.")
