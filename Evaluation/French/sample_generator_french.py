import json
import random
import pandas as pd

# ==================================================
# FILES
# ==================================================

DATASET_JSON = "../Dataset/english_katakana_output.json"

CURRENT_SAMPLE_JSON = "French/sample_100_french.json"

CURRENT_EXCEL = "French/evaluation_results_French.xlsx"

OUTPUT_EXCEL = "French/evaluation_results_French.xlsx"

NEW_NAMES = 400

# ==================================================
# LOAD DATA
# ==================================================

with open(DATASET_JSON, encoding="utf-8") as f:
    dataset = json.load(f)

with open(CURRENT_SAMPLE_JSON, encoding="utf-8") as f:
    current_sample = json.load(f)

df = pd.read_excel(CURRENT_EXCEL)

# ==================================================
# FIND ALREADY USED NAMES
# ==================================================

used = set()

for item in current_sample:
    used.add(
        (
            item["name"],
            item["language"]
        )
    )

# ==================================================
# FILTER REMAINING FRENCH NAMES
# ==================================================

remaining = []

for item in dataset:

    if item["language"] != "French":
        continue

    key = (
        item["name"],
        item["language"]
    )

    if key not in used:
        remaining.append(item)

print(f"Already evaluated : {len(used)}")
print(f"Remaining French  : {len(remaining)}")

# ==================================================
# RANDOM SAMPLE
# ==================================================

new_sample = random.sample(
    remaining,
    min(NEW_NAMES, len(remaining))
)

print(f"Adding {len(new_sample)} new names...")

# ==================================================
# CREATE NEW ROWS
# ==================================================

rows = []

for item in new_sample:

    rows.append({

        "Name": item["name"],

        "Language": item["language"],

        "IPA": item["ipa_original"],

        "Pronunciation": item["pronunciation_original"],

        "System Output": item["outputs"]["hybrid_standard"],

        "Raw Output": item["outputs"]["raw_literal"],

        "Human Rating (1-5)": "",

        "Correct? (Y/N)": "",

        "Expected Katakana": "",

        "Comments": ""

    })

new_df = pd.DataFrame(rows)

# ==================================================
# APPEND
# ==================================================

updated_df = pd.concat(
    [df, new_df],
    ignore_index=True
)

updated_df.to_excel(
    OUTPUT_EXCEL,
    index=False
)

print()
print("Done!")
print(f"Previous rows : {len(df)}")
print(f"Added rows    : {len(new_df)}")
print(f"Total rows    : {len(updated_df)}")