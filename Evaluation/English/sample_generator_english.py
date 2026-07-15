import json
import random
import pandas as pd

# ==================================================
# CONFIG
# ==================================================


DATASET_JSON = "../Dataset/english_katakana_output.json"

CURRENT_SAMPLE_JSON = "English/sample_100_english.json"

CURRENT_EXCEL = "English/evaluation_results_English.xlsx"

OUTPUT_EXCEL = "English/evaluation_results_English.xlsx"

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

used = {
    (item["name"], item["language"])
    for item in current_sample
}

# ==================================================
# FILTER REMAINING ENGLISH NAMES
# ==================================================

english_languages = {
    "English",
    "American English",
    "British English"
}

remaining = []

for item in dataset:

    if item["language"] not in english_languages:
        continue

    key = (
        item["name"],
        item["language"]
    )

    if key not in used:
        remaining.append(item)

print(f"Already evaluated : {len(used)}")
print(f"Remaining English : {len(remaining)}")

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
# APPEND TO EXISTING EXCEL
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
print("======================================")
print("English Evaluation Updated")
print("======================================")
print(f"Previous rows : {len(df)}")
print(f"Added rows    : {len(new_df)}")
print(f"Total rows    : {len(updated_df)}")