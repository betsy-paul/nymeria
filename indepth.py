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

def calculate_metrics(df): # calculate velocity
    # Convert time from microseconds to seconds
    df['time_sec'] = df['time'] / 1e6
    dt = df['time_sec'].diff()
    
    # Euclidean distance between gaze points (Yaw/Pitch) in radians
    # This is the 'Spread' per step
    dist = np.sqrt(df['avg_yaw'].diff()**2 + df['pitch'].diff()**2)
    
    # Velocity = Distance / Time (Radians per second)
    df['velocity'] = dist / dt
    
    # Remove potential infinity if dt is 0
    df['velocity'] = df['velocity'].replace([np.inf, -np.inf], np.nan)
    return df


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

target_tasks = {
    "downloaded_s2_zips": "red",
    "downloaded_s7_zips": "blue"
}
zipToScript = {
    "downloaded_s2_zips": "Where is X",
    "downloaded_s7_zips": "Cooking"
}

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

            df = calculate_metrics(df)
            summary_data.append(df)


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
# fig = px.scatter(
#     summary_df,
#     x="pitch_var",
#     y="yaw_var",
#     color="task",
#     trendline="ols",
#     title="Gaze Variance by Task (Interactive)",
#     hover_data=['task', 'pitch_var', 'yaw_var'] 
# )

# # the threeway plot situation
# fig = px.scatter(
#     summary_df,
#     x="pitch_var",
#     y="yaw_var",
#     color="task",
#     trendline="ols",
#     marginal_x="box",  # Adds a box plot for Pitch distribution at the top
#     marginal_y="violin", # Adds a violin plot for Yaw distribution on the right
#     title="Gaze Variance: Task Comparison with Distributions",
# )

# fig.update_layout(
#     xaxis_title="Pitch Variance",
#     yaxis_title="Yaw Variance",
#     showlegend=True #remove legend since task will show on hover?
# )

# fig.show()

# plotting by category
# category_map = {
#     "downloaded_s2_zips": "Exploration",
#     "downloaded_s3_zips": "Social",
#     "downloaded_s4_zips": "Manual Labor", # Cooking
#     "downloaded_s10_zips": "Manual Labor", # Housekeeping
#     "downloaded_s11_zips": "Manual Labor", # Laundry
#     "downloaded_s12_zips": "Social", # Game Night
#     "downloaded_s13_zips": "Social", # Charades
#     "downloaded_s18_zips": "Locomotion", # Hike
#     "downloaded_s20_zips": "Social"  # Party
# }



# # 2. Apply Mapping (Default to 'Other' if not in list)
# summary_df['category'] = summary_df['task'].map(category_map).fillna("Other")

# # 3. Plot by Category
# fig = px.scatter(
#     summary_df,
#     x="pitch_var",
#     y="yaw_var",
#     color="category",  # Switched from 'task' to 'category'
#     trendline="ols",
#     marginal_x="box",
#     marginal_y="violin",
#     hover_data=['task', 'participant'],
#     title="Gaze Variance by Activity Type",
#     # Specific colors for better contrast
#     color_discrete_map={
#         "Locomotion": "firebrick",
#         "Social": "royalblue",
#         "Manual Labor": "goldenrod",
#         "Exploration": "seagreen",
#         "Other": "gray"
#     }
# )

# fig.update_layout(
#     xaxis_title="Vertical Variance (Pitch)",
#     yaxis_title="Horizontal Variance (Yaw)",
#     legend_title="Activity Category"
# )

# fig.show()

# 1. Define the specific tasks you want to keep
selected_tasks = {
    "downloaded_s2_zips":  {"label": "Where is X",     "cat": "Exploration"},
    "downloaded_s3_zips":  {"label": "Welcome/Place",  "cat": "Social"},
    "downloaded_s4_zips":  {"label": "Cooking",        "cat": "Manual Labor"},
    "downloaded_s8_zips":  {"label": "Having a Meal",  "cat": "Social"},
    "downloaded_s10_zips": {"label": "Housekeeping",   "cat": "Manual Labor"},
    "downloaded_s11_zips": {"label": "Laundry",        "cat": "Manual Labor"},
    "downloaded_s12_zips": {"label": "Game Night",     "cat": "Social"},
    "downloaded_s13_zips": {"label": "Charades",       "cat": "Social"},
    "downloaded_s18_zips": {"label": "Hike",           "cat": "Locomotion"},
    "downloaded_s20_zips": {"label": "Party",          "cat": "Social"}
}

# 2. Filter the dataframe
filtered_df = summary_df[summary_df['task'].isin(selected_tasks.keys())].copy()

# 3. Add readable labels and categories
filtered_df['task_name'] = filtered_df['task'].map(lambda x: selected_tasks[x]['label'])
filtered_df['category'] = filtered_df['task'].map(lambda x: selected_tasks[x]['cat'])

# 4. Plot
fig = px.scatter(
    filtered_df,
    x="pitch_var",
    y="yaw_var",
    color="task_name",      # Color by specific task
    symbol="category",      # Different shapes for different categories (circles vs diamonds)
    trendline="ols",        # Trendlines for each of the 10 tasks
    marginal_x="box",
    marginal_y="violin",
    title="Gaze Variance: Comparison of 10 Selected Nymeria Tasks",
    labels={"pitch_var": "Vertical (Pitch) Variance", "yaw_var": "Horizontal (Yaw) Variance"}
)

fig.update_layout(height=700, legend_title="Tasks & Categories")
fig.show()

print(filtered_df.groupby('task_name')[['pitch_var', 'yaw_var']].mean().sort_values(by='yaw_var', ascending=False))

# Create the comprehensive statistics summary
# We go back to full_df to get the raw velocity/spread averages
stats_report = (
    full_df[full_df['script'].isin(selected_tasks.keys())]
    .groupby("script")
    .agg(
        avg_velocity=("velocity", "mean"),
        yaw_spread=("avg_yaw", lambda x: x.max() - x.min()),
        pitch_spread=("pitch", lambda x: x.max() - x.min()),
        avg_yaw_var=("avg_yaw", "var"),
        avg_pitch_var=("pitch", "var")
    )
    .reset_index()
)

# Map the readable names
stats_report['task_name'] = stats_report['script'].map(lambda x: selected_tasks[x]['label'])

# Sort by velocity to see which task is the most 'active'
print("\n--- FINAL TASK STATISTICS ---")
print(stats_report[['task_name', 'avg_velocity', 'yaw_spread', 'pitch_spread']].sort_values(by='avg_velocity', ascending=False))