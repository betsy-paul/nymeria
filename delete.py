import os
import zipfile
import shutil

# Paths
zip_folder = "downloaded_s20_zips"
target_subpath = "recording_head/mps/eye_gaze/personalized_eye_gaze.csv"

# #checking the folder content
# for zip_name in os.listdir(zip_folder):
#     if zip_name.endswith(".zip"):
#         zip_path = os.path.join(zip_folder, zip_name)
#         with zipfile.ZipFile(zip_path, 'r') as zip_ref:
#             print(f"\nContents of {zip_name}:")
#             for name in zip_ref.namelist():
#                 print(f"  {name}")
#         break  # Just inspect the first ZIP for now

# Loop through ZIPs
for zip_name in os.listdir(zip_folder):
    if zip_name.endswith(".zip"):
        zip_path = os.path.join(zip_folder, zip_name)
        temp_extract_dir = os.path.join(zip_folder, "temp_extract")
        os.makedirs(temp_extract_dir, exist_ok=True)

        print(f"Processing: {zip_name}")
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_contents = zip_ref.namelist()
                if target_subpath in zip_contents:
                    print(f"  Found target file: {target_subpath}")
                    zip_ref.extract(target_subpath, temp_extract_dir)

                    # Create new ZIP with only the target file
                    new_zip_path = os.path.join(zip_folder, f"temp_{zip_name}")
                    with zipfile.ZipFile(new_zip_path, 'w') as new_zip:
                        full_extracted_path = os.path.join(temp_extract_dir, target_subpath)
                        new_zip.write(full_extracted_path, arcname=target_subpath)

                    # Replace original ZIP
                    os.remove(zip_path)
                    os.rename(new_zip_path, zip_path)
                    print(f"  Replaced original ZIP with slimmed version.")
                else:
                    print(f"  Target file not found in: {zip_name}")
        except Exception as e:
            print(f"  Error processing {zip_name}: {e}")

        # Clean up temp folder
        shutil.rmtree(temp_extract_dir)

#note that for s1, 5 people did not have personalised eye gaze
# s3 lost 8 peoople bc no personalised
#s4 lost 1 person
#s5 lost 3
#s6 lost 1
#s7 154 - 137
#s8 lost 10
#s9 lost 0
#s10 lost 7
#s11 lost 3
#s12 lost 5
#s13 lost 2
#s14 lost 3
#s15 lost 3
#s16 lost 126-108 = 18
#s17 lost 5
#s18 lost 6
#s19 lost 10
#s20 lost 6