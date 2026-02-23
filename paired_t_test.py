''' 
This script performs a paired t-test on fixation durations to compare 
Encoding and Recognition sessions across all patients.

We use a paired t-test because we are comparing the same subjects under 
two different conditions. The analysis calculates the mean duration for 
each task per patient and finds the individual differences. 

By comparing the average of these differences against the variation (noise), 
the test maps the result onto a T-distribution curve. The P-value represents 
the area under this curve. '''

import pickle
import numpy as np
import pandas as pd
from scipy import stats


pkl_path = r'e:\eyetracking\pkl\isolated_eye_events.pkl'


def run_fixation_stats(path):
    with open(path, 'rb') as f:
        master_dict = pickle.load(f)

    patient_results = []

    for pid, runs in master_dict.items():
        enc_durations = []
        rec_durations = []
        for run_key in ['R1', 'R2']:
            if run_key not in runs:
                continue
            sessions = runs[run_key]
            for e in sessions.get('Encoding', []):
                if e.get('type') == 'Fixation':
                    enc_durations.append(e['duration'])
            for e in sessions.get('Recognition', []):
                if e.get('type') == 'Fixation':
                    rec_durations.append(e['duration'])

        if enc_durations and rec_durations:
            patient_results.append({
                'Patient': pid,
                'Encoding_Mean': np.mean(enc_durations),
                'Recognition_Mean': np.mean(rec_durations)
            })

    df = pd.DataFrame(patient_results)
    
    # Running the Paired T-Test
    # This compares each patient to themselves
    t_stat, p_val = stats.ttest_rel(df['Encoding_Mean'], df['Recognition_Mean'])

    print(f"Paired T-Test Results (n={len(df)})")
    print(f"Enc Mean: {df['Encoding_Mean'].mean():.4f}s")
    print(f"Rec Mean: {df['Recognition_Mean'].mean():.4f}s")
   
    print(f"T-statistic: {t_stat:.4f}")
    print(f"P-value: {p_val:.4f}")

    return df

# Execute
stats_df = run_fixation_stats(pkl_path)