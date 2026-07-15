import pandas as pd

# ==========================================
# CONFIG
# ==========================================

FILES = {
    "English": "English/evaluation_results_English.xlsx",
    "French": "French/evaluation_results_French.xlsx"
}

# ==========================================
# LEVENSHTEIN
# ==========================================

def levenshtein(a, b):
    dp = [[0]*(len(b)+1) for _ in range(len(a)+1)]

    for i in range(len(a)+1):
        dp[i][0] = i

    for j in range(len(b)+1):
        dp[0][j] = j

    for i in range(1, len(a)+1):
        for j in range(1, len(b)+1):
            cost = 0 if a[i-1] == b[j-1] else 1
            dp[i][j] = min(
                dp[i-1][j] + 1,
                dp[i][j-1] + 1,
                dp[i-1][j-1] + cost
            )

    return dp[-1][-1]

# ==========================================
# LOAD & CALCULATE (LOOP OVER LANGUAGES)
# ==========================================

print("="*50)
print("CHARACTER ERROR RATE")
print("="*50)

# Iterate over both items in the dictionary
for language, file_path in FILES.items():
    
    try:
        df = pd.read_excel(file_path)
        
        # Clean data
        df = df.dropna(subset=["Expected Katakana"])
        df["System Output"] = df["System Output"].fillna("")

        errors = 0
        characters = 0

        for _, row in df.iterrows():
            pred = str(row["System Output"])
            gold = str(row["Expected Katakana"])

            errors += levenshtein(pred, gold)
            characters += len(gold)

        cer = (errors / characters) if characters > 0 else 0

        # Print results for the current language
        print(f"\nLanguage : {language}")
        print(f"CER : {cer:.4f}")
        
    except FileNotFoundError:
        print(f"\nLanguage : {language}")
        print(f"Error: The file '{file_path}' was not found. Please check your folder structure.")