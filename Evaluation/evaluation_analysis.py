import pandas as pd
import json
from collections import Counter

# --------------------------------------------------
# CONFIG
# --------------------------------------------------

# ==========================================
# CONFIG
# ==========================================

#LANGUAGE = "English"
LANGUAGE = "French"

EXCEL_FILE = f"{LANGUAGE}/evaluation_results_{LANGUAGE}.xlsx"

if LANGUAGE == "English":
    JSON_FILE = "English/sample_100_English.json"
elif LANGUAGE == "French":
    JSON_FILE = "French/sample_100_French.json"
else:
    raise ValueError("Unsupported language.")
# --------------------------------------------------
# LOAD FILES
# --------------------------------------------------

df = pd.read_excel(EXCEL_FILE)

with open(JSON_FILE, "r", encoding="utf-8") as f:
    json_data = json.load(f)

# Remove unrated rows
df = df.dropna(subset=["Human Rating (1-5)"])
df["Human Rating (1-5)"] = df["Human Rating (1-5)"].astype(int)

total = len(df)

# --------------------------------------------------
# BASIC STATISTICS
# --------------------------------------------------

print("=" * 60)
print(f"{LANGUAGE.upper()} KATAKANA TRANSLATION EVALUATION")
print("=" * 60)

print(f"\nTotal evaluated names : {total}")
print(f"Average score         : {df['Human Rating (1-5)'].mean():.2f}/5")

print("\n=== SCORE DISTRIBUTION ===")

distribution = (
    df["Human Rating (1-5)"]
    .value_counts()
    .sort_index(ascending=False)
)

for score in [5, 4, 3, 2, 1]:

    count = distribution.get(score, 0)

    print(
        f"Score {score}: "
        f"{count:3d} "
        f"({count/total*100:.1f}%)"
    )

excellent = len(df[df["Human Rating (1-5)"] >= 4])
acceptable = len(df[df["Human Rating (1-5)"] == 3])
poor = len(df[df["Human Rating (1-5)"] <= 2])

print("\n=== PERFORMANCE ===")

print(
    f"Successful (4-5): {excellent} ({excellent/total*100:.1f}%)"
)
print(
    f"Acceptable (3):   {acceptable} ({acceptable/total*100:.1f}%)"
)
print(
    f"Poor (1-2):       {poor} ({poor/total*100:.1f}%)"
)

accuracy = excellent / total * 100

print(f"\nOverall Accuracy : {accuracy:.2f}%")

# --------------------------------------------------
# ERROR ANALYSIS
# --------------------------------------------------

print("\n=== LOWEST SCORING NAMES ===")

poor_rows = df[df["Human Rating (1-5)"] <= 2]

ipa_counter = Counter()

for _, row in poor_rows.iterrows():

    print("-" * 50)
    print(f"Name      : {row['Name']}")
    print(f"Language  : {row['Language']}")
    print(f"Output    : {row['System Output']}")
    print(f"Expected  : {row['Expected Katakana']}")
    print(f"Score     : {row['Human Rating (1-5)']}")

    if pd.notna(row["Comments"]) and str(row["Comments"]).strip():
        print(f"Comment   : {row['Comments']}")

    for item in json_data:

        if (
            item["name"] == row["Name"]
            and item["language"] == row["Language"]
        ):

            print(
                "IPA       :",
                " ".join(item["analysis"]["ipa_array_raw"])
            )

            for syllable in item["analysis"]["ipa_array_raw"]:
                ipa_counter.update(list(syllable))

            break

# --------------------------------------------------
# IPA SYMBOL ANALYSIS
# --------------------------------------------------

print("\n=== IPA SYMBOLS FOUND IN LOW-SCORING NAMES ===")

for symbol, count in ipa_counter.most_common():
    print(f"{symbol}: {count}")

# --------------------------------------------------
# RULES TO REVIEW
# --------------------------------------------------

print("\n=== SUGGESTED RULES TO REVIEW ===")

ignore = {
    "ˈ",
    "ˌ",
    ".",
    "/"
}

for symbol, count in ipa_counter.most_common():

    if symbol in ignore:
        continue

    if count >= 2:
        print(f"Review rule for: {symbol}")

print("\nEvaluation completed.")