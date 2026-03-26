import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Define the folder containing all JSON files
folder_path = r"C:\Users\Betsy\OneDrive\Documents\GitHub\nymeria/downloaded_metadata"


# Initialize a list to store age group data
age_groups = []

# Loop through all JSON files in the folder
for filename in os.listdir(folder_path):
    if filename.endswith(".json"):  # Ensure it's a JSON file
        file_path = os.path.join(folder_path, filename)
        
        with open(file_path, "r") as f:
            data = json.load(f)

        # Extract participant age group if available
        participant_age_group = data.get("participant_age_group")
        if participant_age_group:  # Only store valid entries
            age_groups.append(participant_age_group)

# Convert to a DataFrame for visualization
df = pd.DataFrame(age_groups, columns=["participant_age_group"])
# Define the custom age group order so it prints in a specific order
age_order = ["18-24", "25-30", "31-35", "36-40", "41-45", "46-50"]
# Convert to a categorical variable with ordered levels
df["participant_age_group"] = pd.Categorical(df["participant_age_group"], categories=age_order, ordered=True)


# Plot histogram of age distribution
plt.figure(figsize=(8,6))
sns.histplot(df["participant_age_group"], bins=len(age_order), discrete=True)
plt.title("Age Group Distribution in Nymeria Dataset")
plt.xlabel("Age Group")
plt.ylabel("Count")
plt.xticks(rotation=44)  # Rotate labels for readability
plt.show()