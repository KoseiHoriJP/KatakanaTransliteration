import pandas as pd

# ==========================================
# CONFIG
# ==========================================

LANGUAGE = "English"
LANGUAGE = "French"

EXCEL_FILE = f"{LANGUAGE}/evaluation_results_{LANGUAGE}.xlsx"

# ==========================================
# LOAD
# ==========================================

df = pd.read_excel(EXCEL_FILE)

df = df.dropna(subset=["Expected Katakana"])

# ==========================================
# CHARACTER ACCURACY
# ==========================================

correct = 0
total = 0

for _, row in df.iterrows():

    pred = str(row["System Output"])
    gold = str(row["Expected Katakana"])

    max_len = max(len(pred), len(gold))

    total += max_len

    for p, g in zip(pred, gold):
        if p == g:
            correct += 1

accuracy = correct / total * 100

# ==========================================
# RESULTS
# ==========================================

print("="*50)
print("CHARACTER ACCURACY")
print("="*50)

print(f"\nLanguage : {LANGUAGE}")
print(f"Accuracy : {accuracy:.2f}%")
