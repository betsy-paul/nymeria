import pandas as pd
import requests
import os
import json
import zipfile
import io
import seaborn as sns
import matplotlib.pyplot as plt
from collections import defaultdict
import numpy as np
from scipy.stats import gaussian_kde
import statistics
from scipy.ndimage import gaussian_filter
import plotly.express as px #for the hover in graph

# 2 Where_is_x 118 YES 
# 3 Welcome_to_my_place YES
# Cooking 154 YES
# 8 Having_a_meal 53 YES
# 10 Housekeeping 79 YES
# 11 Laundary 28 YES
# 12 Game_night 113 YES
# 13 Charades 27 YES
# 18 Hike 25 YES
# 20 Party 67 YES

# summary statistics: gaze velocity, spread and plot all 

ZIPS_DIR = "downloaded_s2_zips"


BASE_DIR = os.getcwd()  # Looks in the 'nymeria' folder where your script is
summary_data = []

# this whole section should be uncommented for plotting individual tasks
def process_zip_to_dataframe(zip_bytes, subject_id, script_name):
    print(f"[CALL] process_zip_to_dataframe for {subject_id}")
    try:
        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zip_file:
            print(f"\n[PATH SCAN] {subject_id} → ZIP contains:")

            expected_csv_path = "recording_head/mps/eye_gaze/personalized_eye_gaze.csv"
            found_eye_gaze_file = False
            df = None # Initialize df to None

            for file_in_zip in zip_file.namelist():
                print("   •", file_in_zip)

                normalized_file_path = file_in_zip.replace("\\", "/")

                if normalized_file_path == expected_csv_path:
                # if "eye_gaze" in file_in_zip.replace("\\", "/") and file_in_zip.endswith("personalized_eye_gaze.csv"):
                    print(f"[FOUND] personalized_eye_gaze.csv for {subject_id}")
                    with zip_file.open(file_in_zip) as f:
                        df = pd.read_csv(f)
                        print(f"[DEBUG] Columns in {subject_id}'s CSV: {df.columns.tolist()}")

                    # Check if expected columns exist
                    if "left_yaw_rads_cpf" in df.columns and "right_yaw_rads_cpf" in df.columns and "pitch_rads_cpf" in df.columns:
                        df["avg_yaw"] = (df["left_yaw_rads_cpf"] + df["right_yaw_rads_cpf"]) / 2
                        df = df.rename(columns={
                            "tracking_timestamp_us": "time",
                            "pitch_rads_cpf": "pitch"
                        })
                        df = df[["time", "avg_yaw", "pitch"]]
                        df["subject_id"] = subject_id
                        df["script"] = script_name
                        print(f"[INFO] Successfully parsed {df.shape[0]} rows from {expected_csv_path}")
                        return df
                    else:
                        print(f"[SKIP] Missing yaw/pitch columns in {file_in_zip} for {subject_id}. Available columns: {df.columns.tolist()}")
                        return None
                    
        if not found_eye_gaze_file:
            print(f"[MISS] No personalized_eye_gaze.csv at {expected_csv_path} in ZIP for {subject_id}")
        return None
    
    except zipfile.BadZipFile:
        print(f"[FAIL] Bad ZIP file for {subject_id}. The file is likely corrupted or not a ZIP archive.")
        return None

def process_zip_and_extract_angles(zip_bytes, subject_id, script_name):
    print(f"[CALL] process_zip_and_extract_angles for {subject_id}")

    df = process_zip_to_dataframe(zip_bytes, subject_id, script_name)

    if df is not None and "avg_yaw" in df.columns and "pitch" in df.columns:
        print(f"[INFO] Extracted {df.shape[0]} rows for {subject_id} ({script_name})")
        return df
    else:
        print(f"[SKIP] No valid pitch/yaw data for {subject_id}") ## wdym mean this is not different
        return None

def plot_individual_heatmap(zip_path, subject_id, script_name):
    with open(zip_path, 'rb') as f:
        zip_bytes = f.read()

    df = process_zip_and_extract_angles(zip_bytes, subject_id, script_name)

    if df is None or df.empty:
        print(f"[SKIP] No valid data to plot for {subject_id}")
        return

    df = df.dropna(subset=["avg_yaw", "pitch"])
    if df.empty:
        print(f"[SKIP] All data is NaN for {subject_id}")
        return

# ZIPS_DIR = "downloaded_s2_zips"
# script_name = "S2-Where_is_X"

target_tasks = {
    "downloaded_s2_zips": "red",
    "downloaded_s7_zips": "blue"
}
zipToScript = {
    "downloaded_s2_zips": "Where is X",
    "downloaded_s7_zips": "Cooking"
}


# all_data = []
# processed_count = 0

# for zip_filename in os.listdir(ZIPS_DIR):
#     if not zip_filename.endswith(".zip"):
#         continue

#     subject_id = os.path.splitext(zip_filename)[0]
#     zip_path = os.path.join(ZIPS_DIR, zip_filename)

#     print(f"[CACHE] Using cached ZIP for {subject_id} from {zip_path}")
#     with open(zip_path, 'rb') as f:
#         zip_bytes = f.read()

#     df_angles = process_zip_and_extract_angles(zip_bytes, subject_id, script_name)

#     if df_angles is not None:
#         all_data.append(df_angles)
#         processed_count += 1
#         print(f"[ADD] Appended data for {subject_id}")
#     else:
#         print(f"[MISS] No usable angles data for {subject_id}")

# print("\n All downloads complete.")
# print(f"Successfully processed data for {processed_count} sequences.")

summary_data = []
BASE_DIR = os.getcwd() #set this NYMERIA directory to be where we look

for task_name in os.listdir(BASE_DIR):
    task_path = os.path.join(BASE_DIR, task_name)
    if not os.path.isdir(task_path):
        continue

    for zip_filename in os.listdir(task_path):
        if not zip_filename.endswith(".zip"):
            continue

        subject_id = os.path.splitext(zip_filename)[0]
        zip_path = os.path.join(task_path, zip_filename)

        with open(zip_path, "rb") as f:
            zip_bytes = f.read()

        df = process_zip_and_extract_angles(zip_bytes, subject_id, task_name)

        if df is not None:
            pitch_var = df["pitch"].var()
            yaw_var = df["avg_yaw"].var()

            summary_data.append(df
            # {
            #     "participant": subject_id,
            #     "task": task_name,
            #     "pitch_var": pitch_var,
            #     "yaw_var": yaw_var
            # }
            )


# Combine all participant-task DataFrames
if not summary_data:
    print("[ERROR] No valid data collected. Check earlier logs for issues.")
    exit()

full_df = pd.concat(summary_data, ignore_index=True)
print(f"[INFO] Combined DataFrame shape: {full_df.shape}")
print(full_df[["subject_id", "script", "pitch", "avg_yaw"]].head())

# Drop rows with missing values
full_df = full_df.dropna(subset=["pitch", "avg_yaw"])

# Compute variance per participant-task pair
summary_df = (
    full_df
    .groupby(["subject_id", "script"])
    .agg(pitch_var=("pitch", "var"), yaw_var=("avg_yaw", "var"))
    .reset_index()
    .rename(columns={"subject_id": "participant", "script": "task"})
)

print(f"[INFO] Summary DataFrame:\n{summary_df.head()}")

## FOR PLOTLY PLOTS YOU CAN ONLY PLOT ONE AT A TIME? COMMENT THE OTHER ONES
# use plotly for scatter plot by participant
fig = px.scatter(
    summary_df,
    x="pitch_var",
    y="yaw_var",
    color="participant",
    title="Gaze Variance by Participant (Interactive)",
    hover_data=['participant', 'pitch_var', 'yaw_var'] 
)

fig.update_layout(
    xaxis_title="Pitch Variance",
    yaxis_title="Yaw Variance",
    showlegend=False #remove legend since participant name will show on hover
)

fig.show()

# use plotly for scatter plot by task
fig = px.scatter(
    summary_df,
    x="pitch_var",
    y="yaw_var",
    color="task",
    title="Gaze Variance by Task (Interactive)",
    hover_data=['task', 'pitch_var', 'yaw_var'] 
)

fig.update_layout(
    xaxis_title="Pitch Variance",
    yaxis_title="Yaw Variance",
    showlegend=False #remove legend since task will show on hover
)

fig.show()

# # Plot 1: Color by task
# plt.figure(figsize=(8, 6))
# sns.scatterplot(data=summary_df, x="pitch_var", y="yaw_var", hue="task", palette="tab10", s=100)
# plt.title("Gaze Variance by Task")
# plt.xlabel("Pitch Variance")
# plt.ylabel("Yaw Variance")
# plt.grid(True)
# plt.tight_layout()
# plt.show()

# # Plot 2: Color by participant
# plt.figure(figsize=(8, 6))
# sns.scatterplot(data=summary_df, x="pitch_var", y="yaw_var", hue="participant", palette="husl", s=100)
# plt.title("Gaze Variance by Participant")
# plt.xlabel("Pitch Variance")
# plt.ylabel("Yaw Variance")
# plt.grid(True)
# plt.tight_layout()
# plt.show()

# for _, row in summary_df.iterrows():
#     plt.text(row["pitch_var"], row["yaw_var"], row["participant"], fontsize=8, ha='right', va='bottom')

# plt.title("Gaze Variance by Task")
# plt.xlabel("Pitch Variance")
# plt.ylabel("Yaw Variance")
# plt.grid(True)
# plt.tight_layout()
# plt.show()

# plt.figure(figsize=(8, 6))

# # Plot lines connecting each participant’s tasks
# for participant, group in summary_df.groupby("participant"):
#     plt.plot(group["pitch_var"], group["yaw_var"], marker='o', label=participant, alpha=0.5)

# plt.title("Participant Gaze Variance Trajectories")
# plt.xlabel("Pitch Variance")
# plt.ylabel("Yaw Variance")
# plt.grid(True)
# plt.tight_layout()
# plt.show()

# sns.scatterplot(data=summary_df, x="pitch_var", y="yaw_var", hue="task", palette="tab10", s=100)