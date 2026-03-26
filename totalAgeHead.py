import json 
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from collections import defaultdict


# this script loads JSON files containing head trajectory data for all sujects of Nymeria, 
# separates it into age groups, and visualizes it using a boxplot.


# # Load JSON files
# ages = ["young_Nymeria", "middle_Nymeria", "older_Nymeria"]
# dataframes = {} #store values obtained in a dict
# dataframes = [] #store values in list



def getHead(json_dir):
    dataframes = []

    for filename in os.listdir(json_dir):
        if filename.endswith(".json"):

            with open(os.path.join(json_dir, filename), 'r') as f:
                data = json.load(f)
                head_trajectory = data.get("head_trajectory_m")
                participant_age_group = data.get("participant_age_group", "Unknown")
                df = pd.DataFrame([data])

            if "head_trajectory_m" is not None:
                df = pd.DataFrame([{
                    "head_trajectory_m": data["head_trajectory_m"], 
                    "participant_age_group": participant_age_group
                }])
                dataframes.append(df)
    
    return dataframes

ageVhead = getHead(r"C:\Users\Betsy\OneDrive\Documents\GitHub\nymeria")
print(ageVhead)

# Merge datasets
df_combined = pd.concat(ageVhead, ignore_index=True)

# print data in terminal
print(df_combined.head())

# head trajectory plot
plt.figure(figsize=(8,6))
# sns.scatterplot(x="participant_age_group", y="head_trajectory_m", data=df_combined)
# sns.boxplot(x="participant_age_group", y="head_trajectory_m", data=df_combined)
# sns.stripplot(x="participant_age_group", y="head_trajectory_m", data=df_combined, jitter=True, alpha=0.5, color='blue', size=5)
sns.pointplot(
    x="participant_age_group",
    y="head_trajectory_m",
    data=df_combined,
    capsize=0.1,
    errwidth=1.2,
    join=True
)
plt.title("Mean Head Trajectory Across Age Groups")
plt.ylabel("Mean Head Trajectory (meters)")
plt.xlabel("Age Group")
plt.xticks(rotation=44)  # Rotate labels if needed
plt.show()
