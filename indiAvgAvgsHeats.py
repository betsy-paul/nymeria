import requests
import os
import json
import zipfile
import io
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from collections import defaultdict
import numpy as np
from scipy.stats import gaussian_kde
import statistics
from scipy.ndimage import gaussian_filter

ZIPS_DIR = "downloaded_s7_zips"

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


target_scripts = {
    "S16-Simon_says",
    "S12-Game_night",
    "S7-Cooking"
}

all_data = []


METADATA_DIR = "downloaded_metadata"
os.makedirs(METADATA_DIR, exist_ok=True)
os.makedirs(ZIPS_DIR, exist_ok=True)

json_filepath = "nymeria_download_urls_3Acts.json"

if not os.path.exists(json_filepath):
    print(f"Error: JSON file '{json_filepath}' not found.")
    print("Please ensure 'nymeria_download_urls_3Acts.json' is in the script's directory or provide the full path.")
    exit()

with open(json_filepath, "r") as file:
    data_structure = json.load(file)

sequences = data_structure.get("sequences", {})

# # Filter out any non-participant entries
# valid_subjects = {
#     subject_id: subject_data
#     for subject_id, subject_data in sequences.items()
#     if isinstance(subject_data, dict) and "metadata_json" in subject_data
# }

print(f"Found {len(sequences)} total subjects in JSON to process.")
processed_count = 0

for subject_id, subject_data in sequences.items():
    print(f"\n--- Processing Sequence: {subject_id} ---")

    try:
        metadata_info = subject_data.get("metadata_json", {})
        url = metadata_info.get("download_url")
        filename = metadata_info.get("filename")
        metadata_filepath = os.path.join(METADATA_DIR, filename) # Save to METADATA_DIR

        if not (url and filename):
            print(f"[SKIP] Missing URL or filename for {subject_id}")
            continue


        # Check if metadata is already downloaded
        if os.path.exists(metadata_filepath):
            print(f"[CACHE] Using cached metadata for {subject_id} from {metadata_filepath}")
        else: # download metadata
            print(f"[FETCH] Downloading metadata for {subject_id} from {url}")
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            # if response.status_code != 200:
            #     print(f"[FAIL] Could not download metadata for {subject_id}")
            #     continue

            with open(metadata_filepath, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"[DOWNLOADED] Metadata for {subject_id} → {metadata_filepath}")


        # Parse metadata to get the script name
        with open(metadata_filepath, "r") as f:
            metadata = json.load(f)
        script_name = metadata.get("script")
        # print(f"[FETCH] Downloaded ZIP for {subject_id} ({script_name}), size: {len(response.content)} bytes")


        if not script_name:
            print(f"[WARN] 'script' key not found in metadata for {subject_id}. Skipping.")
            continue

        print(f"[INFO] Subject {subject_id} belongs to script: '{script_name}'")

        if script_name not in target_scripts: # Check against target_scripts
            print(f"[SKIP] Script '{script_name}' for {subject_id} is not one of the target activities ({list(target_scripts)}).")
           # continue


        # Assume you have access to the recording URL (maybe in subject_data?)

        recording_info = subject_data.get("recording_head", {})
        recording_url = recording_info.get("download_url")
        # recording_file = f"{subject_id}_{script_name}_recording.csv"

        zip_filename = f"{subject_id}_{script_name}.zip"
        zip_filepath = os.path.join(ZIPS_DIR, zip_filename)

        if not recording_url:
            print(f"[SKIP] No recording head URL for {subject_id}")
            continue

        # ## START CHANGE ##
        zip_bytes = None
        # Check if the ZIP is already downloaded
        if os.path.exists(zip_filepath):
            print(f"[CACHE] Using cached ZIP for {subject_id} from {zip_filepath}")
            with open(zip_filepath, 'rb') as f:
                zip_bytes = f.read()
        else:
            # Download the recording head file
            print(f"[FETCH] Attempting to download recording head ZIP for {subject_id} ({script_name})...")
            response_rec = requests.get(recording_url)
            response_rec.raise_for_status()

            # Save the downloaded ZIP content to the cache file
            with open(zip_filepath, 'wb') as f:
                f.write(response_rec.content)
            
            zip_bytes = response_rec.content
            print(f"[DOWNLOADED] Recording head ZIP for {subject_id} ({script_name}), size: {len(zip_bytes)} bytes")

        # Now process the ZIP from the `zip_bytes` variable, which comes from either cache or download
        print(f"[ZIP] Extracting angles for {subject_id}")
        df_angles = process_zip_and_extract_angles(zip_bytes, subject_id, script_name)
        # ## END CHANGE ##

        if df_angles is not None:
            all_data.append(df_angles)
            processed_count += 1
            print(f"[ADD] Appended data for {subject_id}")
        else:
        # print(f"[FAIL] Failed to download ZIP for {subject_id}")
            print(f"[MISS] No usable angles data for {subject_id} after ZIP processing.")

    except requests.exceptions.RequestException as e:
        print(f"[FAIL] Network/Download error for {subject_id}: {e}")
        if 'response_rec' in locals() and os.path.exists(zip_filepath):
            os.remove(zip_filepath)
            print(f"[CLEANUP] Removed partial download: {zip_filepath}")
    except json.JSONDecodeError as e:
        print(f"[FAIL] JSON parsing error for metadata of {subject_id}: {e}")
    except Exception as e: # Catch any other unexpected errors
        print(f"[FAIL] An unexpected error occurred for {subject_id}: {e}")

    

print("\n All downloads complete.")
print(f"Successfully processed data for {processed_count} sequences.")

###################################
# makin a heatmaps folder unless it's already there
HEATMAP_OUTPUT_DIR = "heatmaps"
os.makedirs(HEATMAP_OUTPUT_DIR, exist_ok=True)

zip_path = "downloaded_s7_zips/temp_Nymeria_v0.0_20231211_s1_seth_bowman_act1_u7em0v_recording_head.zip"
subject_id = "seth_bowman"
script_name = "S7-Cooking"

with open(zip_path, 'rb') as f:
    zip_bytes = f.read()

df = process_zip_and_extract_angles(zip_bytes, subject_id, script_name)

if df is None or df.empty:
    print(f"[SKIP] No valid data to plot for {subject_id}")
else:
    df = df.dropna(subset=["avg_yaw", "pitch"])
    df["avg_yaw_deg"] = np.degrees(df["avg_yaw"])
    df["pitch_deg"] = np.degrees(df["pitch"])

    if df.empty:
        print(f"[SKIP] All data is NaN for {subject_id}")
    else:
        plt.figure(figsize=(10, 8))
        sns.kdeplot(
            x=df["avg_yaw_deg"],
            y=df["pitch_deg"],
            fill=True,
            cmap="afmhot_r",
            thresh=0.05,
            levels=100,
            alpha=0.7,
            cbar=True,
            cbar_kws={'label': 'Density'}
        )

        plt.title(f"Yaw vs. Pitch Heatmap for {subject_id} ({script_name})")
        plt.xlabel("Average Yaw (degrees)")
        plt.ylabel("Average Pitch (degrees)")
        plt.xlim(-10, 10)
        plt.ylim(-35, -0)
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.tight_layout()


        os.makedirs(HEATMAP_OUTPUT_DIR, exist_ok=True)
        heatmap_filename = os.path.join(HEATMAP_OUTPUT_DIR, f'heatmap_{subject_id}_{script_name}.png')
        plt.savefig(heatmap_filename)
        plt.close()
        print(f"[DONE] Saved individual heatmap to {heatmap_filename}")