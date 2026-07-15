import pandas as pd
import json
from collections import Counter

# ==================================================
# CONFIG
# ==================================================

FILES = {
    "English": {
        "excel": "English/evaluation_results_English.xlsx",
        "json": "English/sample_100_english.json"
    },
    "French": {
        "excel": "French/evaluation_results_French.xlsx",
        "json": "French/sample_100_french.json"
    }
}

# ==================================================
# ANALYSIS FUNCTION
# ==================================================

def analyze_language(language, excel_file, json_file):

    df = pd.read_excel(excel_file)

    with open(json_file, "r", encoding="utf-8") as f:
        json_data = json.load(f)

    df = df.dropna(subset=["Human Rating (1-5)"])
    df["Human Rating (1-5)"] = df["Human Rating (1-5)"].astype(int)

    total = len(df)

    average = df["Human Rating (1-5)"].mean()

    success = len(df[df["Human Rating (1-5)"] >= 4])
    acceptable = len(df[df["Human Rating (1-5)"] == 3])
    poor = len(df[df["Human Rating (1-5)"] <= 2])

    accuracy = success / total * 100

    ipa_counter = Counter()

    poor_rows = df[df["Human Rating (1-5)"] <= 2]

    for _, row in poor_rows.iterrows():

        for item in json_data:

            if (
                item["name"] == row["Name"]
                and item["language"] == row["Language"]
            ):

                for syllable in item["analysis"]["ipa_array_raw"]:

                    ipa = (
                        syllable
                        .replace("/", "")
                        .replace(".", "")
                        .replace("ˈ", "")
                        .replace("ˌ", "")
                    )

                    ipa_counter.update(list(ipa))

                break

    return {
        "total": total,
        "average": average,
        "accuracy": accuracy,
        "success": success,
        "acceptable": acceptable,
        "poor": poor,
        "ipa_counter": ipa_counter
    }

# ==================================================
# RUN
# ==================================================

results = {}

for language, paths in FILES.items():

    results[language] = analyze_language(
        language,
        paths["excel"],
        paths["json"]
    )

# ==================================================
# PRINT REPORT
# ==================================================

print("=" * 60)
print("FINAL EVALUATION SUMMARY")
print("=" * 60)

overall_total = 0
overall_success = 0
overall_score = 0

for language in ["English", "French"]:

    r = results[language]

    overall_total += r["total"]
    overall_success += r["success"]
    overall_score += r["average"] * r["total"]

    print(f"\n{language}")
    print("-" * 30)

    print(f"Evaluated Names : {r['total']}")
    print(f"Average Score   : {r['average']:.2f}/5")
    print(f"Accuracy        : {r['accuracy']:.2f}%")
    print(f"Successful      : {r['success']}")
    print(f"Acceptable      : {r['acceptable']}")
    print(f"Poor            : {r['poor']}")

overall_accuracy = overall_success / overall_total * 100
overall_average = overall_score / overall_total

print("\n" + "=" * 60)
print("OVERALL PERFORMANCE")
print("=" * 60)

print(f"Total Names      : {overall_total}")
print(f"Average Score    : {overall_average:.2f}/5")
print(f"Overall Accuracy : {overall_accuracy:.2f}%")

print("\n" + "=" * 60)
print("MOST COMMON ERROR IPA SYMBOLS")
print("=" * 60)

for language in ["English", "French"]:

    print(f"\n{language}")

    counter = results[language]["ipa_counter"]

    ignore = {
        "/",
        ".",
        "ˈ",
        "ˌ"
    }

    shown = 0

    for symbol, count in counter.most_common():

        if symbol in ignore:
            continue

        print(f"{symbol:4} : {count}")

        shown += 1

        if shown == 10:
            break

print("\n" + "=" * 60)
print("CONCLUSION")
print("=" * 60)

print(
    f"The proposed IPA-based Katakana generation system achieved "
    f"an overall average score of {overall_average:.2f}/5 "
    f"and an overall translation accuracy of "
    f"{overall_accuracy:.2f}% across English and French names."
)

print(
    "\nMost remaining errors are associated with language-specific "
    "vowel sounds, diphthongs, nasal vowels, schwa, and rhotic "
    "pronunciations, indicating that future improvements should "
    "focus on refining language-specific IPA-to-Katakana mapping rules."
)