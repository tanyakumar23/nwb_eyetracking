'''
This is the file for looking at the saccade and fixation data for a few patients (10) to see trends. Plots include
1. Pupil Size 
2. Saccade Duration
3. Saccade Amplitude
4. Saccade Velocity
5. Fixation Duration
6. Correct vs Incorrect Recognition Trials
'''
import os
import numpy as np
import pandas as pd
from pynwb import NWBHDF5IO
from glob import glob
import matplotlib.pyplot as plt
import seaborn as sns

# find path
current_dir = os.path.dirname(os.path.abspath(__file__))

# Looking inside nwb files
search_path = os.path.join(current_dir, 'nwb files', 'sub-CS*', '*.nwb')
all_files = glob(search_path)

print(f"Scanning: {search_path}")
print(f"Found {len(all_files)} NWB files.")

if not all_files:
    print("\nERROR: No files found!")
    print(f"Check that your folder is named exactly 'nwb files' and is inside 'eyetracking'.")
    exit()

# DATA PROCESSING
patient_ids = sorted(list(set([os.path.basename(f).split('_')[0] for f in all_files])))
final_results = []
memory_fixation_analysis = [] # list for comparing fixations by result
count_completed = 0
ignore_list = ['sub-CS53'] # data is not proper

for pid in patient_ids:
    if pid in ignore_list or count_completed >= 10:
        continue
    
    p_files = [f for f in all_files if pid in f]
    if len(p_files) < 2:
        continue 
    
    count_completed += 1
    print(f"Processing {pid}...")

    for f_path in sorted(p_files):
        # check for Encoding (CSR1) vs Recognition (CSR2)
        session = "Encoding" if "CSR1" in f_path else "Recognition"
        try:
            with NWBHDF5IO(f_path, 'r') as io:
                nwbfile = io.read()
                # Accessing the pre-processed behavior module
                beh = nwbfile.processing['behavior']
                
                sac_data = np.asarray(beh['Saccade']['TimeSeries'].data)
                fix_data = np.asarray(beh['Fixation']['TimeSeries'].data)
                fix_times = np.asarray(beh['Fixation']['TimeSeries'].timestamps)
                
                final_results.append({
                    'Patient': pid,
                    'View': session,
                    'Fixation_Dur': np.mean(fix_data[:, 0]), # data is in seconds
                    'Avg_Pupil': np.mean(fix_data[:, 3]),
                    'Saccade_Dur': np.mean(sac_data[:, 0]),
                    'Saccade_Amp': np.mean(sac_data[:, 5]),
                    'Saccade_Velo': np.mean(sac_data[:, 6])
                })

                # Link fixation durations to trial outcomes for recognition phase
                if session == "Recognition" and nwbfile.trials is not None:
                    trials_df = nwbfile.trials.to_dataframe()
                    
                    for _, trial in trials_df.iterrows():
                        acc = trial['response_correct']
                        if pd.isna(acc): continue
                        
                        # Match eye tracking timestamps to the trial window (all in seconds)
                        mask = (fix_times >= trial['start_time']) & (fix_times <= trial['stop_time'])
                        trial_durations = fix_data[mask, 0]
                        
                        if len(trial_durations) > 0:
                            # Label by result: 1 is Correct, 0 is Incorrect
                            memory_fixation_analysis.append({
                                'Patient': pid,
                                'Result': 'Correct' if acc == 1 else 'Incorrect',
                                'Fix_Duration_Sec': np.mean(trial_durations)
                            })

        except Exception as e:
            print(f"Error in {pid}: {e}")

# PLOTTING
if final_results:
    summary_df = pd.DataFrame(final_results)
    # Update metrics label to Seconds
    metrics = [('Fixation_Dur', 'Fixation Duration (s)'), ('Avg_Pupil', 'Pupil Size'),
               ('Saccade_Dur', 'Saccade Duration (s)'), ('Saccade_Amp', 'Saccade Amplitude'),
               ('Saccade_Velo', 'Saccade Velocity')]

    # 1. Baseline Plots (Encoding vs Recognition)
    for col, label in metrics:
        plt.figure(figsize=(10, 6))
        
        sns.barplot(data=summary_df, x='Patient', y=col, hue='View', palette='muted')
        plt.xlabel('Patient ID', labelpad=15)
        plt.ylabel(label)
        plt.xticks(rotation=0) 
        plt.legend(title='Session', loc='upper right')
        plt.tight_layout()
        plt.savefig(os.path.join(current_dir, f"Plot_{col}.png"))
        plt.close()

    # 2. Fixation Proof Plot (Correct vs Incorrect) - Focus on Seconds
    if memory_fixation_analysis:
        proof_df = pd.DataFrame(memory_fixation_analysis)
        plt.figure(figsize=(10, 6))
        
        # Plotting the duration difference in seconds
        sns.barplot(data=proof_df, x='Patient', y='Fix_Duration_Sec', hue='Result', palette='muted')
        plt.xlabel('Patient ID', labelpad=15)
        plt.ylabel('Avg Fixation Duration (s)')
        plt.legend(title='Trial Result', loc='upper right')
        plt.tight_layout()
        plt.savefig(os.path.join(current_dir, "Plot_Fixation_Correct_vs_Incorrect.png"))
        plt.close()
    
    summary_df.to_csv(os.path.join(current_dir, "Patient_Behavior_Audit.csv"), index=False)
    print(f"\nProcessed {count_completed} patients.")