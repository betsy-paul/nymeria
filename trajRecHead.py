import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.animation as animation
import os
import json
import numpy as np
import seaborn as sns

# code for  extracting all head trajectories from JSON files in a directory.
import zipfile
import tempfile

def get_fake_name(json_dir):
    """
    Extracts the fake name from a JSON file.

    Args:
        json_dir (str): dir of JSON file.

    Returns:
        str: The fake name if found, else None.
    """
    fake_names = []
    for filename in os.listdir(json_dir):
        if filename.endswith(".json"):
            json_path = os.path.join(json_dir, filename)
            with open(json_path, 'r') as f:
                data = json.load(f)
                fakename = data.get("fake_name")
                if fakename:
                    fake_names.append(fakename)
    return fake_names


def find_and_load_eye_gaze(fake_name, zip_dir, gaze_type="personalized"):
    """
    Searches for a zip file matching the fake_name, extracts it, and loads the eye gaze CSV.

    Args:
        fake_name (str): The fake name from metadata (e.g., 'kenneth_fischer').
        zip_dir (str): Directory containing the zip files.
        gaze_type (str): 'general' or 'personalized'.

    Returns:
        pd.DataFrame or None: Eye gaze data if found, else None.
    """
    for filename in os.listdir(zip_dir):
        # print(f"Checking: {filename}")
        if filename.endswith(".zip") and fake_name in filename: # 
            zip_path = os.path.join(zip_dir, filename)
            print(f"Opening: {zip_path}")
            # print(f"Is zipfile: {zipfile.is_zipfile(zip_path)}")

            with tempfile.TemporaryDirectory() as temp_dir:
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                    # for root, dirs, files in os.walk(temp_dir):
                    #     for name in files:
                    #         print(os.path.join(root, name))

                # Construct path to eye gaze CSV
                gaze_filename = f"{gaze_type}_eye_gaze.csv"
                gaze_path = os.path.join(temp_dir, "recording_head", "mps", "eye_gaze", gaze_filename)

                if os.path.exists(gaze_path):
                    print(f"Loaded gaze data for {fake_name} from {gaze_filename}")
                    return pd.read_csv(gaze_path)

    # print(f"No matching zip found for {fake_name}")
    return None

#call func
# df_gaze = find_and_load_eye_gaze("kenneth_fischer", "C:\\Users\\Betsy\\OneDrive\\Documents\\GitHub\\nymeria", gaze_type="personalized")

json_dir = "C:\\Users\\Betsy\\OneDrive\\Documents\\GitHub\\nymeria"
zip_dir = "C:\\Users\\Betsy\\OneDrive\\Documents\\GitHub\\nymeria"

loaded_names = set()

for fake_name in get_fake_name(json_dir):
    if fake_name in loaded_names:
        print(f"Skipping {fake_name} — already loaded.")
        continue 
    df_gaze = find_and_load_eye_gaze(fake_name, zip_dir, gaze_type="personalized")
    if df_gaze is not None:
        # should probs do smth with df_gaze, like save it or analyze it
        print(f"Loaded data for {fake_name} with {len(df_gaze)} rows.")
        loaded_names.add(fake_name)
    else:
        print(f"Skipping {fake_name} — no data found.")
        # continue


# left_yaw = find_and_load_eye_gaze("kenneth_fischer", zip_dir, gaze_type="personalized")
# right_yaw = find_and_load_eye_gaze("kenneth_fischer", zip_dir, gaze_type="personalized")
# # avg_yaw = find_and_load_eye_gaze("seth_bowman", zip_dir, gaze_type="personalized")
# pitch = find_and_load_eye_gaze("kenneth_fischer", zip_dir, gaze_type="personalized")

seth_left_yaw = find_and_load_eye_gaze("seth_bowman", zip_dir, gaze_type="personalized")
seth_right_yaw = find_and_load_eye_gaze("seth_bowman", zip_dir, gaze_type="personalized")
seth_pitch = find_and_load_eye_gaze("seth_bowman", zip_dir, gaze_type="personalized")


# Merge datasets
# df_combined = left_yaw #bc left_yaw is already a list. if it was a dataframe, you could use pd.concat([df1, df2], ignore_index=True) or smth
# df_combined = df_combined.rename(columns={ 
#     "tracking_timestamp_us": "time",
#     "left_yaw_rads_cpf": "left_yaw"
# })

seth_df_combined = seth_left_yaw
seth_df_combined = seth_df_combined.rename(columns={
    "tracking_timestamp_us": "seth_time",
    "left_yaw_rads_cpf": "seth_left_yaw"
})

# df_right = right_yaw
# df_right = df_right.rename(columns={
#     "tracking_timestamp_us": "time",
#     "right_yaw_rads_cpf": "right_yaw"
# })

seth_df_right = seth_right_yaw
seth_df_right = seth_df_right.rename(columns={
    "tracking_timestamp_us": "seth_time",
    "right_yaw_rads_cpf": "seth_right_yaw"
})


# df_pitch = pitch
# df_pitch = df_pitch.rename(columns={
#     "tracking_timestamp_us": "time",    
#     "pitch_rads_cpf": "pitch"
# })

seth_df_pitch = seth_pitch
seth_df_pitch = seth_df_pitch.rename(columns={
    "tracking_timestamp_us": "seth_time",
    "pitch_rads_cpf": "seth_pitch"
})


# if "time" in df_combined.columns:
#     df_combined["time_sec"] = df_combined["time"] / 1e6
#     df_right["time_sec"] = df_right["time"] / 1e6
#     df_pitch["time_sec"] = df_pitch["time"] / 1e6
# else:
#     print("No 'time' column found.")

if "seth_time" in seth_df_combined.columns:
    seth_df_combined["seth_time_sec"] = seth_df_combined["seth_time"] / 1e6
    seth_df_right["seth_time_sec"] = seth_df_right["seth_time"] / 1e6
    seth_df_pitch["seth_time_sec"] = seth_df_pitch["seth_time"] / 1e6
else:
    print("No 'seth_time' column found.")

# df_merged = pd.merge(df_combined, df_right[["time", "right_yaw"]], on="time", how="inner")
# df_merged["avg_yaw"] = (df_merged["left_yaw"] + df_merged["right_yaw"]) / 2
# df_pitch = df_pitch[["time", "time_sec", "pitch"]]  # ensure time columns exist

seth_df_merged = pd.merge(seth_df_combined, seth_df_right[["seth_time", "seth_right_yaw"]], on="seth_time", how="inner")
seth_df_merged["seth_avg_yaw"] = (seth_df_merged["seth_left_yaw"] + seth_df_merged["seth_right_yaw"]) / 2 
seth_df_pitch = seth_df_pitch[["seth_time", "seth_pitch"]]  # ensure time columns exist

# df_active = df_combined
# df_righter = df_right
# df_meaner = df_merged
# df_tooLoud = df_pitch

seth_df_active = seth_df_combined
seth_df_righter = seth_df_right
seth_df_meaner = seth_df_merged 
seth_df_tooLoud = seth_df_pitch

# # seth_bowman plot uh not sure why he's special
# df_active = df_combined[(df_combined["time_sec"] > 40000)]  # Filter rows between 40s and 47.4s
# df_righter = df_right[df_right["time_sec"] > 40000]
# # this line doesnt work - df_meaner = df_merged[(df_merged["time_sec"] > 47324.397634) & (df_merged["time_sec"].min()+10)]
# # df_meaner = df_merged[(df_merged["time_sec"] > 47324.397634) & (df_merged["time_sec"] < 47334.397634)]
# df_meaner = df_merged[df_merged["time_sec"] > 40000]
# df_tooLoud = df_pitch[df_pitch["time_sec"] > 40000]

# df_pitchYaw = pd.merge(
#     df_meaner[["time", "avg_yaw", "time_sec"]],
#     df_pitch,
#     on="time",
#     how="inner"
# )

seth_df_pitchYaw = pd.merge(
    seth_df_meaner[["seth_time", "seth_avg_yaw", "seth_time_sec"]],
    seth_df_pitch,
    on="seth_time",
    how="inner"
)

# df_pitchYaw_active = df_pitchYaw
# # df_pitchYaw_active["avg_yaw_zeroed"] = df_pitchYaw_active["avg_yaw"] - df_pitchYaw_active["avg_yaw"].min()
# df_pitchYaw_active["time_sec_zeroed"] = df_pitchYaw_active["time"] - df_pitchYaw_active["time"].min()
# heat_df = df_pitchYaw_active.dropna(subset=["avg_yaw", "pitch"]) #this is for ken, paul works with df_pitchYaw_active

seth_df_pitchYaw_active = seth_df_pitchYaw
# seth_df_pitchYaw_active["seth_avg_yaw_zeroed"] = seth_df_pitchYaw_active["seth_avg_yaw"] - seth_df_pitchYaw_active["seth_avg_yaw"].min()
seth_df_pitchYaw_active["seth_time_sec_zeroed"] = seth_df_pitchYaw_active["seth_time"] - seth_df_pitchYaw_active["seth_time"].min()
seth_heat_df = seth_df_pitchYaw_active.dropna(subset=["seth_avg_yaw", "seth_pitch"]) #this is for seth 


# print data in terminal
# print(df_active.head())
# print(df_righter.head())
# print(df_meaner.head())
# print(df_tooLoud.head())

#print seth_bowman data
print("seth_bowman data:")
print(seth_df_active.head())
print(seth_df_righter.head())
print(seth_df_meaner.head())
print(seth_df_tooLoud.head())

# wanna plot left and right yaw over time for each subject
# plt.figure(figsize=(8,6))
# sns.pointplot(
#     x="time",
#     y="left_yaw",
#     data=df_combined,
#     capsize=0.1,
#     err_kws={'linewidth': 1.2},
#     join=True
# )
# plt.title("left_yaw over time")
# plt.ylabel("left_yaw (radians)")
# plt.xlabel("Time (seconds)")
# plt.xticks(rotation=44)  # Rotate labels if needed
# plt.show()
##################################
max_x = max(seth_heat_df["seth_avg_yaw"].max(), seth_heat_df["seth_avg_yaw"].max())
min_x = min(seth_heat_df["seth_avg_yaw"].min(), seth_heat_df["seth_avg_yaw"].min())

max_y = max(seth_heat_df["seth_pitch"].max(), seth_heat_df["seth_pitch"].max())
min_y = min(seth_heat_df["seth_pitch"].min(), seth_heat_df["seth_pitch"].min())


plt.figure(figsize=(8, 6))


# y1 = heat_df["pitch"] #kenneth pitch
y2 = seth_heat_df["seth_pitch"] #seth pitch

#################################
# # uncomment the following lines to plot a rough heatmap of pitch vs yaw for amanda and seth
# plt.hist2d(
#     heat_df["avg_yaw"],  # X-axis
#     heat_df["pitch"],           # Y-axis
#     bins=400, #resolution
#     cmap='bone_r',
#     alpha=1,  # Adjust transparency to see overlap                      
# )
# plt.colorbar(label='kenneth pitch density')  # Color bar for Amanda's data

plt.hist2d(
    seth_heat_df["seth_avg_yaw"],  # X-axis
    seth_heat_df["seth_pitch"],           # Y-axis
    bins=400, #resolution
    cmap='bone_r',
    alpha=0.6,  # Adjust transparency to see overlap                     
)
plt.colorbar(label='seth pitch density')  # Color bar for Seth's data

plt.title("seth Yaw vs. Pitch Density - Rough Heatmap")

############################
# Uncomment the following lines to plot a smoothed heatmap
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
############################


# plt.xlabel("Average Yaw")
# plt.ylabel("Pitch (radians)")
# plt.legend(loc="upper right")
# plt.tight_layout()
# plt.xlim(min_x, max_x)
# plt.ylim(min_y, max_y)


# seth_patch = mpatches.Patch(color="blue", alpha=0.8, label="Seth")
# amanda_patch = mpatches.Patch(color="orange", alpha=0.4, label="Amanda")  # or colormap match

# plt.legend(handles=[seth_patch, amanda_patch], loc="upper right")

plt.show()

##############################################
# uncomment to have the animated plot of pitch over yaw
# fig, ax = plt.subplots()
# line, = ax.plot([], [], lw=2, color='palegoldenrod', label='Pitch')
# ax.set_xlim(df_pitchYaw_active["avg_yaw"].min(), df_pitchYaw_active["avg_yaw_zeroed"].max())
# ax.set_ylim(df_pitchYaw_active["pitch"].min(), df_pitchYaw_active["pitch"].max())
# ax.set_title("Pitch Over Yaw for Amanda (Animated)")
# ax.set_xlabel("avg yaw")
# ax.set_ylabel("Pitch (rad)") 
# ax.yaxis.label.set_color('goldenrod')

# xdata, ydata = [], []

# def update(frame):
#     xdata.append(df_pitchYaw_active.iloc[frame]["avg_yaw_zeroed"])
#     ydata.append(df_pitchYaw_active.iloc[frame]["pitch"])
#     line.set_data(xdata, ydata)
#     return line,

# # ani = animation.FuncAnimation(fig, update, frames=range(0, len(df_pitchYaw_active), 4), interval=4, blit=True)
# ani = animation.FuncAnimation(fig, update, frames=range(0, len(df_pitchYaw_active), 4), interval=4, blit=True)
# plt.show()
# print("Animation complete.")

################################################################################
## Uncomment the following lines to plot average yaw
# line, = ax.plot([], [], lw=2, color='purple', label='Average Yaw')
# ax.set_xlim(df_meaner["time_sec"].min(), df_meaner["time_sec"].max())
# ax.set_ylim(df_meaner["avg_yaw"].min(), df_meaner["avg_yaw"].max())
# ax.set_title("Average Yaw Over Time (Animated)")
# ax.set_xlabel("Time (s)")
# ax.set_ylabel("Average Yaw (rad)") #writes the actual label
# ax.yaxis.label.set_color('purple')

# xdata, ydata = [], []

# def update(frame):
#     xdata.append(df_meaner.iloc[frame]["time_sec"])
#     ydata.append(df_meaner.iloc[frame]["avg_yaw"])
#     line.set_data(xdata, ydata)
#     return line,

# ani = animation.FuncAnimation(fig, update, frames=range(0, len(df_meaner), 4), interval=4, blit=True)
# plt.show()

################################################################################

# # Uncomment the following lines to plot left and right yaw
# line, = ax.plot([], [], lw=2)
# ax2 = ax.twinx()  # Create a second y-axis for right yaw
# ax2.plot(df_righter["time_sec"], df_righter["right_yaw"], color='red', label='Right Yaw') #fixes right yaw in place so its not animated

# ax.set_xlim(df_active["time_sec"].min(), df_active["time_sec"].max())

# ax.set_ylim(df_active["left_yaw"].min(), df_active["left_yaw"].max())
# ax2.set_ylim(df_righter["right_yaw"].min(), df_righter["right_yaw"].max())

# ax.set_title("Yaw Over Time (Animated)")
# ax.set_xlabel("Time (s)")

# ax.set_ylabel("Left Yaw (rad)")
# ax2.set_ylabel("Right Yaw (rad)")

# ax.yaxis.label.set_color('blue')
# ax2.yaxis.label.set_color('red')

# xdata, ydata = [], []

# def update(frame):
#     xdata.append(df_active.iloc[frame]["time_sec"])
#     ydata.append(df_active.iloc[frame]["left_yaw"])
#     line.set_data(xdata, ydata)
#     return line,

# ani = animation.FuncAnimation(fig, update, frames=range(0, len(df_active), 4), interval=4, blit=True)
# plt.show()