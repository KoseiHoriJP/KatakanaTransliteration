import pandas as pd
from Levenshtein import distance
from difflib import SequenceMatcher

FILES = {
    "English": "English/evaluation_results_English.xlsx",
    "French": "French/evaluation_results_French.xlsx"
}

print("=" * 90)
print("RAW OUTPUT vs HYBRID OUTPUT")
print("=" * 90)

print(
    f"{'Language':<12}"
    f"{'Raw Edit':>12}"
    f"{'Hybrid Edit':>15}"
    f"{'Improvement':>15}"
    f"{'Raw Similarity':>18}"
    f"{'Hybrid Similarity':>20}"
)

print("-" * 90)

overall = {
    "raw_edit": 0,
    "hybrid_edit": 0,
    "raw_sim": 0,
    "hybrid_sim": 0,
    "samples": 0
}

for language, file in FILES.items():

    df = pd.read_excel(file)

    df["Expected Katakana"] = (
        df["Expected Katakana"]
        .replace("", pd.NA)
        .fillna(df["System Output"])
    )

    df = df.dropna(subset=["Human Rating (1-5)"])

    raw_edit = 0
    hybrid_edit = 0

    raw_similarity = 0
    hybrid_similarity = 0

    for _, row in df.iterrows():

        expected = str(row["Expected Katakana"])

        raw = str(row["Raw Output"])

        hybrid = str(row["System Output"])

        raw_edit += distance(raw, expected)

        hybrid_edit += distance(hybrid, expected)

        raw_similarity += SequenceMatcher(
            None,
            raw,
            expected
        ).ratio()

        hybrid_similarity += SequenceMatcher(
            None,
            hybrid,
            expected
        ).ratio()

    total = len(df)

    raw_edit /= total
    hybrid_edit /= total

    raw_similarity = raw_similarity / total * 100
    hybrid_similarity = hybrid_similarity / total * 100

    improvement = (
        (raw_edit - hybrid_edit)
        / raw_edit
        * 100
    )

    overall["raw_edit"] += raw_edit * total
    overall["hybrid_edit"] += hybrid_edit * total
    overall["raw_sim"] += raw_similarity * total
    overall["hybrid_sim"] += hybrid_similarity * total
    overall["samples"] += total

    print(
        f"{language:<12}"
        f"{raw_edit:>12.2f}"
        f"{hybrid_edit:>15.2f}"
        f"{improvement:>14.1f}%"
        f"{raw_similarity:>17.2f}%"
        f"{hybrid_similarity:>19.2f}%"
    )

print("-" * 90)

samples = overall["samples"]

raw_edit = overall["raw_edit"] / samples
hybrid_edit = overall["hybrid_edit"] / samples

raw_sim = overall["raw_sim"] / samples
hybrid_sim = overall["hybrid_sim"] / samples

improvement = (
    (raw_edit - hybrid_edit)
    / raw_edit
    * 100
)

print(
    f"{'Overall':<12}"
    f"{raw_edit:>12.2f}"
    f"{hybrid_edit:>15.2f}"
    f"{improvement:>14.1f}%"
    f"{raw_sim:>17.2f}%"
    f"{hybrid_sim:>19.2f}%"
)

print("=" * 90)