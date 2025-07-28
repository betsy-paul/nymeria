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




# json_dir = "C:\\Users\\Betsy\\OneDrive\\Documents\\GitHub\\nymeria"
ZIPS_DIR = "downloaded_zips"

def process_zip_to_dataframe(zip_bytes, subject_id, script_name):
    # with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zip_file:
    #     print(f"[ZIP CONTENTS for {subject_id}]:")

    #     for file in zip_file.namelist():
    #         print(" →", file)
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

########################################################

# Step 1: Gather and combine pitch/yaw per subject
# script_data = {
#     "S16-Simon_says": [], 
#     "S12-Game_night": [], 
#     "S7-Cooking": []
# }

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


if not all_data:
    print("⚠️ No participant data found. This might be due to:")
    print("   1. 'nymeria_download_urls_3Acts.json' structure not matching expectations.")
    print("   2. Download failures (check error messages above).")
    print("   3. Incorrect `target_scripts` names or metadata parsing.")
    print("   4. The expected CSV file ('recording_head/mps/eye_gaze/personalized_eye_gaze.csv') not being present or having wrong column names inside the ZIPs.")
    exit()

print(f"[SUMMARY] Total valid subjects: {len(all_data)}")
combined_df = pd.concat(all_data, ignore_index=True)


for script in combined_df["script"].unique():
    subset = combined_df[combined_df["script"] == script]

print(f"[DF INFO] Combined DataFrame has {combined_df.shape[0]} rows and columns: {combined_df.columns.tolist()}")

###################################
# makin a heatmaps folder unless it's already there
HEATMAP_OUTPUT_DIR = "heatmaps"
os.makedirs(HEATMAP_OUTPUT_DIR, exist_ok=True)

# ################ ACT HEATMAPS #########################
# for script in combined_df["script"].unique():
#     # Keep subset creation using original radian columns for dropna
#     subset = combined_df[combined_df["script"] == script].dropna(subset=["avg_yaw", "pitch"])

#     if subset.empty:
#         print(f"Skipping heatmap for '{script}' as no valid data remains after dropping NaNs.")
#         continue

#     plt.figure(figsize=(10, 8))
#     sns.kdeplot(
#         x=subset["avg_yaw"], # Plot original radian column
#         y=subset["pitch"],   # Plot original radian column
#         fill=True,
#         cmap="afmhot_r",
#         thresh=0.05,
#         levels=100,
#         alpha=0.7,
#         cbar=True,
#         cbar_kws={'label': 'Density'}
#     )
#     plt.title(f"Yaw vs. Pitch Heatmap for {script}")
#     plt.xlabel("Average Yaw (radians)") # Keep label as radians
#     plt.ylabel("Pitch (radians)")     # Keep label as radians
#     plt.grid(True, linestyle='--', alpha=0.6)
#     plt.tight_layout()
    
#     heatmap_filename = os.path.join(HEATMAP_OUTPUT_DIR, f'heatmap_{script.replace(" ", "_")}.png')
#     plt.savefig(heatmap_filename)
#     plt.close()
#     print(f"Generated heatmap for activity: {script} and saved to {heatmap_filename}")
#     plt.show()

# ######## VARIANCE HEATMAPS #########
# this shows density not variance so scrap it

# for script in combined_df["script"].unique():
#     subset = combined_df[combined_df["script"] == script].dropna(subset=["avg_yaw", "pitch"])

#     if subset.empty:
#         print(f"Skipping heatmap for '{script}' due to insufficient data.")
#         continue

#     data = subset[["avg_yaw", "pitch"]].to_numpy().T  # Shape: (2, N)
#     kde = gaussian_kde(data)
    
#     # Create a grid over yaw/pitch space
#     x_min, x_max = data[0].min(), data[0].max()
#     y_min, y_max = data[1].min(), data[1].max()
#     X, Y = np.meshgrid(
#         np.linspace(x_min, x_max, 100),
#         np.linspace(y_min, y_max, 100)
#     )
#     positions = np.vstack([X.ravel(), Y.ravel()])
#     Z = np.reshape(kde(positions), X.shape)

#     # Plotting the KDE result as heatmap
#     plt.figure(figsize=(10, 8))

#     plt.imshow(
#         Z.T,
#         origin='lower',
#         extent=[x_min, x_max, y_min, y_max],
#         cmap="afmhot_r",
#         aspect='auto'
#     )

#     plt.colorbar(label='Variance Density')
#     plt.title(f"Variance Heatmap of Gaze: {script}")
#     plt.xlabel("Average Yaw (radians)")
#     plt.ylabel("Pitch (radians)")
#     plt.grid(True, linestyle='--', alpha=0.4)
#     plt.tight_layout()

#     outpath = os.path.join(HEATMAP_OUTPUT_DIR, f'variance_heatmap_{script.replace(" ", "_")}.png')
#     plt.savefig(outpath)
#     plt.close()
#     print(f"✅ Saved variance heatmap for {script} → {outpath}")


######### OTHER VARIANCE HEATMAPS #####
yaw_range = subset["avg_yaw"].max() - subset["avg_yaw"].min()
pitch_range = subset["pitch"].max() - subset["pitch"].min()

max_range = max(yaw_range, pitch_range)
# BIN_COUNT = int(np.ceil(max_range / 0.03491)) # - 2 degree
BIN_COUNT = int(np.ceil(max_range / 0.0174533)) # - 1 degree
# BIN_COUNT = int(np.ceil(max_range / 0.00873)) - half a degree
# BIN_COUNT = 100  #  hard coded bin, increase for resolution

for script in combined_df["script"].unique():
    subset = combined_df[combined_df["script"] == script].dropna(subset=["avg_yaw", "pitch", "subject_id"])

    if subset.empty:
        print(f"Skipping variance map for '{script}' due to missing data.")
        print(f"skipping mean map for '{script}' due to missing data.")
        continue

    # Bin both axes
    yaw_bins = np.linspace(subset["avg_yaw"].min(), subset["avg_yaw"].max(), BIN_COUNT + 1)
    pitch_bins = np.linspace(subset["pitch"].min(), subset["pitch"].max(), BIN_COUNT + 1)

    subset["yaw_bin"] = pd.cut(subset["avg_yaw"], bins=yaw_bins, labels=False, include_lowest=True)
    subset["pitch_bin"] = pd.cut(subset["pitch"], bins=pitch_bins, labels=False, include_lowest=True)


    # this is the key hehehehe
    count_matrix = defaultdict(lambda: defaultdict(int))  # {(yaw_bin, pitch_bin): {subject_id: count}}
    # - The outer defaultdict lets you access bins by a (yaw_bin, pitch_bin) key.
    # - Each outer bin contains an inner defaultdict(int) to track how many times each subject_id looked into it.
    # count_matrix[(12, 33)] = { #inner code bc ik you're gonna forget how we got here
    #     "amanda": 2,
    #     "kenneth": 5,
    #     "seth": 1
    # }

    for _, row in subset.iterrows():
        bin_key = (row["yaw_bin"], row["pitch_bin"])
        subject = row["subject_id"]
        if pd.notnull(bin_key[0]) and pd.notnull(bin_key[1]):
            count_matrix[bin_key][subject] += 1

    # # creat 2d grid for plot
    grid = np.full((BIN_COUNT, BIN_COUNT), np.nan)

    for (i, j), subject_counts in count_matrix.items():
        counts = list(subject_counts.values())
        total_bin_count = sum(counts)

        if total_bin_count < 4:
            grid[j, i] = np.nan  # Optional: explicitly mark sparse bins
            continue

        if len(counts) > 1:
            grid[j, i] = np.log(np.var(counts) + 0.001)
        else:
            grid[j, i] = 0  # Or np.nan if you want to ignore bins with a single subject
    
    smoothed_grid = gaussian_filter(grid, sigma=1.0)

    plt.figure(figsize=(10, 8))
    plt.imshow(
        grid,
        origin='lower',
        extent=[yaw_bins.min(), yaw_bins.max(), pitch_bins.min(), pitch_bins.max()],
        cmap="afmhot_r",
        aspect="auto",
    )

    # plt.colorbar(label="Local Gaze Variance")
    plt.colorbar(label="Logged Gaze Variance")
    plt.title(f"Local Variance of Gaze: {script}")
    plt.xlabel("Average Yaw (radians)")
    plt.ylabel("Pitch (radians)")
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()

    outpath = os.path.join(HEATMAP_OUTPUT_DIR, f"gaze_variance_map_{script.replace(' ', '_')}.png")
    plt.savefig(outpath)
    plt.close()
    print(f"📈 Saved spatial variance map for {script} → {outpath}")


    ############## STUFF FOR THE MEAN MAPS, scratch that, MEDIAN now ###################
    # mean_grid = np.full((BIN_COUNT, BIN_COUNT), np.nan)
    # median_grid = np.full((BIN_COUNT, BIN_COUNT), np.nan)



    # for (i, j), subject_counts in count_matrix.items():
    #     counts = list(subject_counts.values())
    #     total_bin_count = sum(counts)

    #     unique_subject_count = len(subject_counts)

    #     if unique_subject_count < 3: # or total_bin_count < 2:
    #         continue


    #     mean_grid[j, i] = np.mean(counts)
    #     median_grid[j,i] = np.median(counts)

    # # filled_bins = np.count_nonzero(~np.isnan(median_grid))
    # # print(f"✅ Bins with median data: {filled_bins}")

    # plt.figure(figsize=(10, 8))
    # plt.imshow(
    #     median_grid,
    #     origin='lower',
    #     extent=[yaw_bins.min(), yaw_bins.max(), pitch_bins.min(), pitch_bins.max()],
    #     cmap="afmhot_r",
    #     aspect="auto",
    # )
    # plt.colorbar(label="Median Gaze Frequency")
    # plt.title(f"Median Gaze Density: {script}")
    # plt.xlabel("Average Yaw (radians)")
    # plt.ylabel("Pitch (radians)")
    # plt.grid(True, linestyle='--', alpha=0.5)
    # plt.tight_layout()

    # median_outpath = os.path.join(HEATMAP_OUTPUT_DIR, f"gaze_median_map_{script.replace(' ', '_')}.png")
    # plt.savefig(median_outpath)
    # plt.close()
    # print(f"Saved median gaze map for {script} → {median_outpath}")
    
    ###############################
    # plt.figure(figsize=(10, 8))
    # plt.imshow(
    #     mean_grid,
    #     origin='lower',
    #     extent=[yaw_bins.min(), yaw_bins.max(), pitch_bins.min(), pitch_bins.max()],
    #     cmap="afmhot_r",
    #     aspect="auto",
    # )
    # plt.colorbar(label="Mean Gaze Frequency")
    # plt.title(f"Mean Gaze Density: {script}")
    # plt.xlabel("Average Yaw (radians)")
    # plt.ylabel("Pitch (radians)")
    # plt.grid(True, linestyle='--', alpha=0.5)
    # plt.tight_layout()

    # mean_outpath = os.path.join(HEATMAP_OUTPUT_DIR, f"gaze_mean_map_{script.replace(' ', '_')}.png")
    # plt.savefig(mean_outpath)
    # plt.close()
    # print(f"Saved mean gaze map for {script} → {mean_outpath}")



# ##################################
# max_x = max(heat_df["avg_yaw"].max(), seth_heat_df["seth_avg_yaw"].max())
# min_x = min(heat_df["avg_yaw"].min(), seth_heat_df["seth_avg_yaw"].min())

# max_y = max(heat_df["pitch"].max(), seth_heat_df["seth_pitch"].max())
# min_y = min(heat_df["pitch"].min(), seth_heat_df["seth_pitch"].min())


# plt.figure(figsize=(8, 6))


# y1 = heat_df["pitch"] #amanda pitch
# y2 = seth_heat_df["seth_pitch"] #seth pitch

# #################################

# sns.kdeplot(
#     x=df_pitchYaw_active["avg_yaw"],
#     y=seth_df_pitchYaw_active["seth_pitch"],
#     fill=True,
#     cmap="Blues",
#     thresh=0.05,
#     levels=100,
#     alpha = 0.8,
#     label="Seth",
# )

# sns.kdeplot(
#     x=df_pitchYaw_active["avg_yaw"],
#     y=df_pitchYaw_active["pitch"],
#     fill=True,
#     cmap="afmhot_r",
#     thresh=0.05,
#     levels=100,
#     alpha = 0.4,
#     label="Amanda"
# )

# plt.title("Amanda Yaw vs. Pitch – Smoothed Heatmap")

# plt.show()