# ==========================================
# This checks if the expected output is same as system output. Because it only checks if its same or not even a small  error counted as fialirue output. 
# ==========================================


import pandas as pd

# ==========================================
# FILES TO EVALUATE
# ==========================================

FILES = {
    "English": "English/evaluation_results_English.xlsx",
    "French": "French/evaluation_results_French.xlsx"
}

print("=" * 60)
print("EXACT MATCH ACCURACY")
print("=" * 60)

overall_total = 0
overall_correct = 0

for language, file in FILES.items():

    print(f"\n{language}")

    # ------------------------------
    # Load file
    # ------------------------------

    df = pd.read_excel(file)

    # Remove rows without an expected answer
    df = df.dropna(subset=["Expected Katakana"])

    df["Expected Katakana"] = (
        df["Expected Katakana"]
        .astype(str)
        .str.strip()
    )

    df["System Output"] = (
        df["System Output"]
        .astype(str)
        .str.strip()
    )

    # Ignore blank expected outputs
    df = df[df["Expected Katakana"] != ""]

    total = len(df)

    correct = (
        df["System Output"] ==
        df["Expected Katakana"]
    ).sum()

    accuracy = (
        correct / total * 100
        if total > 0
        else 0
    )

    overall_total += total
    overall_correct += correct

    print(f"Evaluated : {total}")
    print(f"Exact Match : {correct}")
    print(f"Accuracy : {accuracy:.2f}%")

# ==========================================
# OVERALL RESULT
# ==========================================

overall_accuracy = (
    overall_correct / overall_total * 100
    if overall_total > 0
    else 0
)

print("\n" + "=" * 60)
print("OVERALL")
print("=" * 60)

print(f"Total Evaluated : {overall_total}")
print(f"Exact Matches   : {overall_correct}")
print(f"Overall Accuracy: {overall_accuracy:.2f}%")