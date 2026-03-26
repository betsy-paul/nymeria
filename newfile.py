import pandas as pd
import os
import zipfile
import io
import plotly.express as px

# 1. SETUP: Define your tasks and their colors
# Ensure these match your folder names exactly (e.g., "S7-Cooking", "S2-Where_is_X")
target_tasks = {
    "downloaded_s2_zips": "red",
    "downloaded_s7_zips": "blue",
    "downloaded_s20_zips": "yellow"
}

BASE_DIR = os.getcwd()  # Looks in the 'nymeria' folder where your script is
summary_data = []

# --- Standard Extraction Functions ---

def process_zip_to_dataframe(zip_bytes, subject_id, script_name):
    try:
        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zip_file:
            expected_csv_path = "recording_head/mps/eye_gaze/personalized_eye_gaze.csv"
            for file_in_zip in zip_file.namelist():
                if file_in_zip.replace("\\", "/") == expected_csv_path:
                    with zip_file.open(file_in_zip) as f:
                        df = pd.read_csv(f)
                    
                    if all(col in df.columns for col in ["left_yaw_rads_cpf", "right_yaw_rads_cpf", "pitch_rads_cpf"]):
                        df["avg_yaw"] = (df["left_yaw_rads_cpf"] + df["right_yaw_rads_cpf"]) / 2
                        df = df.rename(columns={"pitch_rads_cpf": "pitch"})
                        df["task"] = script_name
                        return df[["avg_yaw", "pitch", "task"]]
    except Exception as e:
        print(f"[ERROR] Could not process {subject_id}: {e}")
    return None

# --- Main Data Collection Loop ---

print("Scanning for tasks...")
for folder_name in os.listdir(BASE_DIR):
    # Only process if the folder is one of our target tasks
    if folder_name in target_tasks:
        task_path = os.path.join(BASE_DIR, folder_name)
        if not os.path.isdir(task_path):
            continue
            
        print(f"  -> Processing Task: {folder_name}")
        
        for zip_filename in os.listdir(task_path):
            if zip_filename.endswith(".zip"):
                subject_id = os.path.splitext(zip_filename)[0]
                zip_full_path = os.path.join(task_path, zip_filename)
                
                with open(zip_full_path, "rb") as f:
                    zip_bytes = f.read()
                
                df = process_zip_to_dataframe(zip_bytes, subject_id, folder_name)
                
                if df is not None:
                    summary_data.append({
                        "participant": subject_id,
                        "task": folder_name,
                        "pitch_var": df["pitch"].var(),
                        "yaw_var": df["avg_yaw"].var()
                    })

# --- Final Plotting ---

if not summary_data:
    print("[ERROR] No data found. Check your folder names in 'target_tasks'.")
else:
    summary_df = pd.DataFrame(summary_data)

    clean_names = {
        "downloaded_s2_zips": "Where_is_X",
        "downloaded_s7_zips": "Cooking",
        "downloaded_s20_zips": "Party"
    }

    summary_df['task'] = summary_df['task'].replace(clean_names)

    target_tasks = {
        "Where_is_X": "red",
        "Cooking": "blue",
        "Party": "yellow"
    }
    
    # Use color_discrete_map to force your specific red/blue colors
    fig = px.scatter(
        summary_df,
        x="pitch_var",
        y="yaw_var",
        color="task",
        color_discrete_map=target_tasks,
        title="Gaze Variance Comparison: Cooking vs. Where_is_X vs. Party",
        hover_data=['participant', 'task', 'pitch_var', 'yaw_var'],
        template="plotly_white"
    )

    # Hard-set the axes to 0 - 0.1 as requested
    fig.update_xaxes(range=[0, 0.1])
    fig.update_yaxes(range=[0, 0.1])

    fig.update_layout(
        xaxis_title="Pitch Variance",
        yaxis_title="Yaw Variance",
        legend_title="Activity Task"
    )

    fig.show()