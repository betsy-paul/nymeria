import os
import json
from collections import defaultdict
import seaborn as sns
import matplotlib.pyplot as plt

def summarize_nymeria_metadata(json_dir):
    """
    Summarizes Nymeria dataset metadata by counting unique subjects and their associated acts.

    Args:
        json_dir (str): Path to the directory containing JSON metadata files.

    Returns:
        dict: Summary including total files, unique subjects, and act counts per subject.
    """
    subject_acts = defaultdict(set)
    total_files = 0

    for filename in os.listdir(json_dir):
        if filename.endswith(".json"):
            total_files += 1
            with open(os.path.join(json_dir, filename), 'r') as f:
                data = json.load(f)
                fake_name = data.get("fake_name")
                act_id = data.get("act_id")
                if fake_name is not None and act_id is not None:
                    subject_acts[fake_name].add(act_id)

    summary = {
        "total_files": total_files,
        "unique_subjects": len(subject_acts),
        "acts_per_subject": {sid: sorted(list(acts)) for sid, acts in subject_acts.items()}
    }

    return summary

# Usage example
subjectSummary = summarize_nymeria_metadata(r"C:\Users\Betsy\OneDrive\Documents\GitHub\nymeria")
print(subjectSummary)

#{'total_files': 1100, 'unique_subjects': 236, 'acts_per_subject': blahblah, run it again}