import pandas as pd
from difflib import SequenceMatcher

# ==========================================================
# FILES
# ==========================================================

FILES = {
    "English": "English/evaluation_results_English.xlsx",
    "French": "French/evaluation_results_French.xlsx"
}

# ==========================================================
# FUNCTION
# ==========================================================

def similarity(a, b):
    return SequenceMatcher(None, str(a), str(b)).ratio()

# ==========================================================
# EVALUATION
# ==========================================================

overall_scores = []
overall_samples = 0

print("=" * 60)
print("STRING SIMILARITY EVALUATION")
print("=" * 60)

for language, file in FILES.items():

    df = pd.read_excel(file)

    # Blank expected means the system output is correct
    df["Expected Katakana"] = (
        df["Expected Katakana"]
        .replace("", pd.NA)
        .fillna(df["System Output"])
    )

    # Keep only rated samples
    df = df.dropna(subset=["Human Rating (1-5)"])

    scores = []

    for _, row in df.iterrows():

        pred = row["System Output"]
        exp = row["Expected Katakana"]

        score = similarity(pred, exp)
        scores.append(score)

    avg = sum(scores) / len(scores)

    overall_scores.extend(scores)
    overall_samples += len(scores)

    print()
    print(language)
    print(f"Samples            : {len(scores)}")
    print(f"Average Similarity : {avg:.4f}")
    print(f"Percentage         : {avg*100:.2f}%")

# ==========================================================
# OVERALL
# ==========================================================

overall = sum(overall_scores) / len(overall_scores)

print("\n" + "=" * 60)
print("OVERALL")
print("=" * 60)

print(f"Total Samples      : {overall_samples}")
print(f"Average Similarity : {overall:.4f}")
print(f"Percentage         : {overall*100:.2f}%")