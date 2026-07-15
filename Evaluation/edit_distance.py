import pandas as pd

# ==========================================
# CONFIG
# ==========================================

# Define a list of languages to iterate through
LANGUAGES = ["English", "French"]

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
# LOAD & RESULTS (LOOP OVER LANGUAGES)
# ==========================================

print("="*50)
print("EDIT DISTANCE")
print("="*50)

# Loop through each language in the list
for language in LANGUAGES:
    
    # Dynamically build the file path for the current language
    file_path = f"{language}/evaluation_results_{language}.xlsx"
    
    try:
        df = pd.read_excel(file_path)

        # Clean data and prevent blank cells from being read as the literal string "nan"
        df = df.dropna(subset=["Expected Katakana"])
        df["System Output"] = df["System Output"].fillna("")

        distances = []

        for _, row in df.iterrows():

            pred = str(row["System Output"])
            gold = str(row["Expected Katakana"])

            distances.append(levenshtein(pred, gold))

        print(f"\nLanguage         : {language}")
        
        # Prevent ZeroDivisionError and ValueError on empty lists
        if distances:
            print(f"Average Distance : {sum(distances)/len(distances):.2f}")
            print(f"Maximum Distance : {max(distances)}")
            print(f"Minimum Distance : {min(distances)}")
        else:
            print("No valid data found to calculate distances.")
            
    except FileNotFoundError:
        print(f"\nLanguage         : {language}")
        print(f"Error: The file '{file_path}' was not found. Please check your folder structure.")