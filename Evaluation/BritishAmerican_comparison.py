import pandas as pd
from Levenshtein import distance
from difflib import SequenceMatcher

# ==================================================
# CONFIG
# ==================================================

FILE = "English/evaluation_results_English.xlsx"

# ==================================================
# FUNCTIONS
# ==================================================

def character_accuracy(predicted, expected):
    if len(expected) == 0:
        return 1.0
    return max(0, 1 - distance(predicted, expected) / len(expected))


def cer(predicted, expected):
    if len(expected) == 0:
        return 0
    return distance(predicted, expected) / len(expected)


def similarity(predicted, expected):
    return SequenceMatcher(None, predicted, expected).ratio()


# ==================================================
# LOAD DATA
# ==================================================

df = pd.read_excel(FILE)

# Blank expected means the prediction was correct
df["Expected Katakana"] = (
    df["Expected Katakana"]
    .replace("", pd.NA)
    .fillna(df["System Output"])
)

df = df.dropna(subset=["Human Rating (1-5)"])
df["Human Rating (1-5)"] = df["Human Rating (1-5)"].astype(int)

# ==================================================
# EVALUATE EACH LANGUAGE
# ==================================================

print("=" * 90)
print("ENGLISH LANGUAGE VARIANT EVALUATION")
print("=" * 90)

print(
    f"{'Language':<22}"
    f"{'Samples':>10}"
    f"{'Avg Score':>12}"
    f"{'Human Acc':>12}"
    f"{'Exact':>10}"
    f"{'Char Acc':>12}"
    f"{'CER':>10}"
    f"{'Similarity':>14}"
)

print("-" * 90)

languages = sorted(df["Language"].unique())

for lang in languages:

    subset = df[df["Language"] == lang]

    total = len(subset)

    avg_score = subset["Human Rating (1-5)"].mean()

    human_acc = (
        (subset["Human Rating (1-5)"] >= 4).mean() * 100
    )

    exact = 0
    char_scores = []
    cer_scores = []
    sim_scores = []

    for _, row in subset.iterrows():

        pred = str(row["System Output"])
        exp = str(row["Expected Katakana"])

        if pred == exp:
            exact += 1

        char_scores.append(
            character_accuracy(pred, exp)
        )

        cer_scores.append(
            cer(pred, exp)
        )

        sim_scores.append(
            similarity(pred, exp)
        )

    exact = exact / total * 100

    char_acc = sum(char_scores) / total * 100

    cer_avg = sum(cer_scores) / total

    sim_avg = sum(sim_scores) / total * 100

    print(
        f"{lang:<22}"
        f"{total:>10}"
        f"{avg_score:>12.2f}"
        f"{human_acc:>11.2f}%"
        f"{exact:>9.2f}%"
        f"{char_acc:>11.2f}%"
        f"{cer_avg:>10.3f}"
        f"{sim_avg:>13.2f}%"
    )

print("=" * 90)