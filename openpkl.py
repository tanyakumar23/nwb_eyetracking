'''
This file opens the pickle file and prints the first 5 events for Patient 41 (Encoding)
'''
import pickle
import os

# 1. Define where the file is
output_folder = r'E:\eyetracking\nwb files'
pkl_path = os.path.join(output_folder, 'isolated_eye_events.pkl')

# 2. Open (Load) the data
# 'rb' means Read Binary (required for pickle files)
with open(pkl_path, 'rb') as f:
    master_dict = pickle.load(f)

# 3. Quick Sanity Check
# Let's look at the first 5 events for Patient 41 (Encoding)
print("Previewing sub-CS41 Encoding Data:")
preview = master_dict['sub-CS41']['Encoding'][:5]

for event in preview:
    print(f"Type: {event['event']} | Start: {event['start']:.3f} | End: {event['end']:.3f}")

# 4. Count total events found for all patients
print("\n--- Summary ---")
for pid, sessions in master_dict.items():
    enc_count = len(sessions['Encoding'])
    rec_count = len(sessions['Recognition'])

    print(f"Patient {pid}: {enc_count} events in Encoding, {rec_count} events in Recognition")
