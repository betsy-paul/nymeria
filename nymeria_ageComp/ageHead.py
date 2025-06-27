import json 
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# this script loads JSON files containing head trajectory data for different age groups of Nymeria, 
# processes the data, and visualizes it using a boxplot.


# # Load JSON files
# ages = ["young_Nymeria", "middle_Nymeria", "older_Nymeria"]
# dataframes = {} #store values obtained in a dict
# dataframes = [] #store values in list


#load and define json files
files = ["young_Nymeria.json", "middle_Nymeria.json", "old_Nymeria.json"]
dataframes = []

for file in files:
    with open(file, "r") as f:
        data = json.load(f)

    # get age group data
    participant_age_group = data.get("participant_age_group", "Unknown")

    # Convert JSON to DataFrame
    df = pd.DataFrame([data])

    # Keep only head trajectory
    # Ensure head_trajectory_m is properly extracted
    if "head_trajectory_m" in data:
        df = pd.DataFrame([{"head_trajectory_m": data["head_trajectory_m"], "participant_age_group": participant_age_group}])
        dataframes.append(df)

# Merge datasets
df_combined = pd.concat(dataframes, ignore_index=True)

# print data in terminal
print(df_combined.head())

# head trajectory plot
plt.figure(figsize=(8,6))
sns.boxplot(x="participant_age_group", y="head_trajectory_m", data=df_combined)
plt.title("Head Trajectory Across Age Groups")
plt.ylabel("Head Trajectory (meters)")
plt.xlabel("Age Group")
plt.xticks(rotation=44)  # Rotate labels if needed
plt.show()
