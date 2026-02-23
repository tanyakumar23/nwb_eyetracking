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
plot_folder = os.path.join(current_dir, 'plots')
os.makedirs(plot_folder, exist_ok=True)

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
    if not p_files:
        continue 
    
    count_completed += 1
    print(f"Processing {pid}...")

    for f_path in sorted(p_files):
        try:
            with NWBHDF5IO(f_path, 'r') as io:
                nwbfile = io.read()
                beh = nwbfile.processing['behavior']

                # Encoding/recognition windows from trials (sorted by time: row 0 = encoding, rest = recognition)
                trials = nwbfile.intervals['trials']
                starts = np.asarray(trials['start_time'].data[:])
                stops = np.asarray(trials['stop_time'].data[:])
                order = np.argsort(starts)
                starts, stops = starts[order], stops[order]
                enco_start, enco_stop = float(starts[0]), float(stops[0])
                reco_start, reco_stop = float(starts[1]), float(stops[-1])

                sac_ts = np.asarray(beh['Saccade']['TimeSeries'].timestamps[:])
                sac_data = np.asarray(beh['Saccade']['TimeSeries'].data[:])
                fix_ts = np.asarray(beh['Fixation']['TimeSeries'].timestamps[:])
                fix_data = np.asarray(beh['Fixation']['TimeSeries'].data[:])

                def fully_in_window(ts, data_col0, win_start, win_stop):
                    """Mask: events fully inside window (start and end in window)."""
                    starts = ts
                    ends = ts + data_col0
                    return (starts >= win_start) & (ends <= win_stop)

                # Encoding phase: only events fully inside encoding window
                enc_fix = fully_in_window(fix_ts, fix_data[:, 0], enco_start, enco_stop)
                enc_sac = fully_in_window(sac_ts, sac_data[:, 0], enco_start, enco_stop)
                if enc_fix.any() or enc_sac.any():
                    final_results.append({
                        'Patient': pid,
                        'View': 'Encoding',
                        'Fixation_Dur': np.mean(fix_data[enc_fix, 0]) if enc_fix.any() else np.nan,
                        'Avg_Pupil': np.mean(fix_data[enc_fix, 3]) if enc_fix.any() else np.nan,
                        'Saccade_Dur': np.mean(sac_data[enc_sac, 0]) if enc_sac.any() else np.nan,
                        'Saccade_Amp': np.mean(sac_data[enc_sac, 5]) if enc_sac.any() else np.nan,
                        'Saccade_Velo': np.mean(sac_data[enc_sac, 6]) if enc_sac.any() else np.nan,
                    })

                # Recognition phase: only events fully inside recognition window
                rec_fix = fully_in_window(fix_ts, fix_data[:, 0], reco_start, reco_stop)
                rec_sac = fully_in_window(sac_ts, sac_data[:, 0], reco_start, reco_stop)
                if rec_fix.any() or rec_sac.any():
                    final_results.append({
                        'Patient': pid,
                        'View': 'Recognition',
                        'Fixation_Dur': np.mean(fix_data[rec_fix, 0]),
                        'Avg_Pupil': np.mean(fix_data[rec_fix, 3]) if rec_fix.any() else np.nan,
                        'Saccade_Dur': np.mean(sac_data[rec_sac, 0]) if rec_sac.any() else np.nan,
                        'Saccade_Amp': np.mean(sac_data[rec_sac, 5]) if rec_sac.any() else np.nan,
                        'Saccade_Velo': np.mean(sac_data[rec_sac, 6]) if rec_sac.any() else np.nan,
                    })

                # Link fixation durations to trial outcomes (recognition trials only)
                trials_df = trials.to_dataframe()
                trials_df = trials_df.sort_values('start_time').reset_index(drop=True)
                # Only recognition rows (row 0 is encoding, rest are recognition)
                reco_trials = trials_df.iloc[1:]
                for _, trial in reco_trials.iterrows():
                        acc = trial['response_correct']
                        if pd.isna(acc): continue
                        
                        mask = (fix_ts >= trial['start_time']) & (fix_ts <= trial['stop_time'])
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
        plt.savefig(os.path.join(plot_folder, f"Plot_{col}.png"))
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
        plt.savefig(os.path.join(plot_folder, "Plot_Fixation_Correct_vs_Incorrect.png"))
        plt.close()
    
    summary_df.to_csv(os.path.join(plot_folder, "Patient_Behavior_Audit.csv"), index=False)
    print(f"\nProcessed {count_completed} patients.")