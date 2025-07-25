import json
import requests

with open("nymeria_1011.json", "r") as file:
    data = json.load(file)

# Sample JSON data structure (replace with actual data loading)
# data = {
#     "20230607_s0_james_johnson_act1_7xwm28": {
#         "metadata_json": {
#             "download_url": "https://scontent.xx.fbcdn.net/m1/v/t6/An_hhJNNa4sk1VvqkqS9eRoFWSM-fRME4W_8_Rkg05izC59G5SH-S8MuiSw38Fm4XFWH4lFy-B_vMkGM9pRrOS1lG3POgSjWZg",
#             "filename": "Nymeria_v0.0_20230607_s0_james_johnson_act1_7xwm28_metadata.json"
#         }
#     },
#     "20230607_s0_james_johnson_act0_e72nhq": {
#         "metadata_json": {
#             "download_url": "https://scontent.xx.fbcdn.net/m1/v/t6/An-h6phjsDvyUhKBeU2PbJ26_QaprWwMMORvZGZJK_VJedDNyeYqSMpE02UbW4VECwBeqd0lNaCVKKTG1xLBYHf4ruhwxqeL00K",
#             "filename": "Nymeria_v0.0_20230607_s0_james_johnson_act0_e72nhq_metadata.json"
#         }
#     }
# }

if "sequences" not in data:
    print("Error: 'sequences' key not found in JSON file.")
    exit()

sequences = data["sequences"]  # Now we safely access 'sequences'

# Iterate through subjects and download metadata JSON files
for subject_id, subject_data in sequences.items():
    if "metadata_json" in subject_data:
        url = subject_data["metadata_json"]["download_url"]
        filename = subject_data["metadata_json"]["filename"]

        if url and filename:
            response = requests.get(url)

            if response.status_code == 200:
                with open(filename, "wb") as file:
                    file.write(response.content)
                print(f"Downloaded {filename}")
            else:
                print(f"Failed to download {filename}")
        else:
            print(f"no url or filename for {subject_id}")
    else: 
        print(f"no metadata_json found for {subject_id}") # or print("no metadata_json found for + str(subject_id)")

print("Download process complete!")