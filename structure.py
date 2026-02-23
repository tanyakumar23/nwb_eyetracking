'''
This script provides an audit tool to inspect different NWB fields in one place.
It checks high-level behavior metrics, raw eye positions, and the trial timeline.
'''
from pynwb import NWBHDF5IO
import pandas as pd
import os

# file path
f_path = r'E:\000623\sub-CS51\sub-CS51_ses-P51CSR1_behavior+ecephys.nwb'

if os.path.exists(f_path):
    with NWBHDF5IO(f_path, 'r') as io:
        nwb = io.read()

        # SECTION 1: BEHAVIOR METRICS
        # Accesses derived data like Fixation, Saccade, or Blink
        print("SECTION 1: BEHAVIOR METRICS")
        beh_module = nwb.processing['behavior']
        target_metric = 'Fixation' # Options: 'Fixation', 'Saccade', 'Blink'
        
        if target_metric in beh_module.keys():
            data_obj = beh_module[target_metric]
            ts = data_obj['TimeSeries']
            print(f"Investigating {target_metric}:")
            for field in ts.fields.keys():
                if field == 'data':
                    print(f"Data Snippet (First 5): \n{ts.data[:5]}")
                else:
                    # Prints metadata like unit and description
                    print(f"{field}: {getattr(ts, field)}")
        
        

        # SECTION 2: RAW EYE POSITIONS
        # Accesses raw X and Y spatial coordinates
        print("SECTION 2: RAW EYE POSITIONS")
        eye_tracking = nwb.processing['behavior']['EyeTracking']
        spatial = eye_tracking.spatial_series['SpatialSeries']
        
        print(f"Units: {spatial.unit}")
        print(f"Reference Frame: {spatial.reference_frame}")
        print(f"Raw Coordinates (X, Y) Snippet: \n{spatial.data[:5]}")
        
        

        # SECTION 3: EXPERIMENTAL TRIALS
        # Accesses the intervals table for trial timing and results
        print("SECTION 3: TRIALS")
        trials = nwb.intervals['trials']
        trials_df = trials.to_dataframe()
        
        # Prints first 5 trials
        print(trials_df.head())
else:
    print("Path not found.")


#print(nwbfile.processing['behavior']['TimeSeries'].fields.keys())    
