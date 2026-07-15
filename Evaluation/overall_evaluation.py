import pandas as pd
from Levenshtein import distance
from difflib import SequenceMatcher

# ==========================================================
# FILES
# ==========================================================

FILES = {
    "English": "English/evaluation_results_English.xlsx",
    "French": "French/evaluation_results_French.xlsx"
}

# ==========================================================
# FUNCTIONS
# ==========================================================

def character_accuracy(predicted, expected):
    if len(expected) == 0:
        return 1.0

    dist = distance(predicted, expected)

    return max(
        0,
        1 - dist / len(expected)
    )


def cer(predicted, expected):
    if len(expected) == 0:
        return 0

    return distance(predicted, expected) / len(expected)


def string_similarity(predicted, expected):
    return SequenceMatcher(
        None,
        predicted,
        expected
    ).ratio()


# ==========================================================
# EVALUATION
# ==========================================================

results = {}

overall_samples = 0
overall_score = 0
overall_human_correct = 0
overall_exact = 0
overall_char = 0
overall_similarity = 0
overall_cer = 0
overall_edit = 0
overall_poor = 0

for language, file in FILES.items():

    df = pd.read_excel(file)

    # Blank expected means same as system output
    df["Expected Katakana"] = (
        df["Expected Katakana"]
        .replace("", pd.NA)
        .fillna(df["System Output"])
    )

    df = df.dropna(subset=["Human Rating (1-5)"])

    df["Human Rating (1-5)"] = (
        df["Human Rating (1-5)"]
        .astype(int)
    )

    total = len(df)

    avg_score = df["Human Rating (1-5)"].mean()

    human_accuracy = (
        (df["Human Rating (1-5)"] >= 4)
        .mean()
        * 100
    )

    exact_matches = 0

    character_scores = []
    similarity_scores = []
    cer_scores = []
    edit_scores = []

    for _, row in df.iterrows():

        pred = str(row["System Output"])
        exp = str(row["Expected Katakana"])

        if pred == exp:
            exact_matches += 1

        character_scores.append(
            character_accuracy(pred, exp)
        )

        similarity_scores.append(
            string_similarity(pred, exp)
        )

        cer_scores.append(
            cer(pred, exp)
        )

        edit_scores.append(
            distance(pred, exp)
        )

    exact_match = exact_matches / total * 100

    char_acc = (
        sum(character_scores)
        / total
        * 100
    )

    similarity = (
        sum(similarity_scores)
        / total
        * 100
    )

    cer_avg = (
        sum(cer_scores)
        / total
    )

    edit_avg = (
        sum(edit_scores)
        / total
    )

    poor = len(
        df[df["Human Rating (1-5)"] <= 2]
    )

    results[language] = {

        "samples": total,

        "avg_score": avg_score,

        "human_accuracy": human_accuracy,

        "exact_match": exact_match,

        "char_acc": char_acc,

        "similarity": similarity,

        "cer": cer_avg,

        "edit": edit_avg,

        "poor": poor

    }

    overall_samples += total

    overall_score += avg_score * total

    overall_human_correct += (
        human_accuracy / 100 * total
    )

    overall_exact += exact_matches

    overall_char += sum(character_scores)

    overall_similarity += sum(similarity_scores)

    overall_cer += sum(cer_scores)

    overall_edit += sum(edit_scores)

    overall_poor += poor


# ==========================================================
# OVERALL
# ==========================================================

overall_avg_score = overall_score / overall_samples

overall_human_accuracy = (
    overall_human_correct
    / overall_samples
    * 100
)

overall_exact_match = (
    overall_exact
    / overall_samples
    * 100
)

overall_character_accuracy = (
    overall_char
    / overall_samples
    * 100
)

overall_similarity = (
    overall_similarity
    / overall_samples
    * 100
)

overall_cer = (
    overall_cer
    / overall_samples
)

overall_edit = (
    overall_edit
    / overall_samples
)


# ==========================================================
# PRINT
# ==========================================================

print("=" * 70)
print("OVERALL KATAKANA TRANSLATION EVALUATION")
print("=" * 70)

print()

print(
    f"{'Metric':<26}"
    f"{'English':>12}"
    f"{'French':>12}"
    f"{'Overall':>12}"
)

print("-" * 70)

print(
    f"{'Samples':<26}"
    f"{results['English']['samples']:>12}"
    f"{results['French']['samples']:>12}"
    f"{overall_samples:>12}"
)

print(
    f"{'Average Score':<26}"
    f"{results['English']['avg_score']:>12.2f}"
    f"{results['French']['avg_score']:>12.2f}"
    f"{overall_avg_score:>12.2f}"
)

print(
    f"{'Human Accuracy (%)':<26}"
    f"{results['English']['human_accuracy']:>11.2f}%"
    f"{results['French']['human_accuracy']:>11.2f}%"
    f"{overall_human_accuracy:>11.2f}%"
)

print(
    f"{'Exact Match (%)':<26}"
    f"{results['English']['exact_match']:>11.2f}%"
    f"{results['French']['exact_match']:>11.2f}%"
    f"{overall_exact_match:>11.2f}%"
)

print(
    f"{'Character Accuracy (%)':<26}"
    f"{results['English']['char_acc']:>11.2f}%"
    f"{results['French']['char_acc']:>11.2f}%"
    f"{overall_character_accuracy:>11.2f}%"
)

print(
    f"{'String Similarity (%)':<26}"
    f"{results['English']['similarity']:>11.2f}%"
    f"{results['French']['similarity']:>11.2f}%"
    f"{overall_similarity:>11.2f}%"
)

print(
    f"{'Character Error Rate':<26}"
    f"{results['English']['cer']:>12.3f}"
    f"{results['French']['cer']:>12.3f}"
    f"{overall_cer:>12.3f}"
)

print(
    f"{'Edit Distance':<26}"
    f"{results['English']['edit']:>12.2f}"
    f"{results['French']['edit']:>12.2f}"
    f"{overall_edit:>12.2f}"
)

print(
    f"{'Poor Outputs':<26}"
    f"{results['English']['poor']:>12}"
    f"{results['French']['poor']:>12}"
    f"{overall_poor:>12}"
)

print("\n" + "=" * 70)