import pandas as pd
from collections import Counter

# ==========================================================
# CONFIGURATION
# ==========================================================

INPUT_FILE = "English/evaluation_results_English.xlsx"

SCORE_COLUMN = "Human Rating (1-5)"

LOW_SCORE_THRESHOLD = 3

# ==========================================================
# LOAD DATA
# ==========================================================

df = pd.read_excel(
    INPUT_FILE,
    engine="openpyxl"
)

df[SCORE_COLUMN] = pd.to_numeric(
    df[SCORE_COLUMN],
    errors="coerce"
)

errors = df[
    df[SCORE_COLUMN] <= LOW_SCORE_THRESHOLD
]

print("=" * 60)
print("KATAKANA TRANSLATION ERROR ANALYSIS")
print("=" * 60)

print(f"\nTotal evaluated : {len(df)}")
print(f"Poor translations : {len(errors)}")

# ==========================================================
# SHOW LOW SCORING NAMES
# ==========================================================

print("\n=== LOW SCORING NAMES ===")

for _, row in errors.iterrows():

    print("-" * 50)

    print(f"Name      : {row['Name']}")
    print(f"Language  : {row['Language']}")
    print(f"IPA       : {row['IPA']}")
    print(f"Output    : {row['System Output']}")
    print(f"Expected  : {row['Expected Katakana']}")
    print(f"Score     : {row[SCORE_COLUMN]}")

# ==========================================================
# IPA SYMBOL ANALYSIS
# ==========================================================

symbol_counter = Counter()

for ipa in errors["IPA"]:

    ipa = (
        str(ipa)
        .replace("/", "")
        .replace(".", "")
        .replace("ˈ", "")
        .replace("ˌ", "")
        .replace(" ", "")
    )

    i = 0

    while i < len(ipa):

        if ipa[i:i+3] in ("t͡ʃ", "d͡ʒ"):

            symbol_counter[ipa[i:i+3]] += 1
            i += 3

        else:

            symbol_counter[ipa[i]] += 1
            i += 1

print("\n=== IPA SYMBOLS IN LOW SCORING NAMES ===")

for symbol, count in symbol_counter.most_common():

    print(f"{symbol:4} : {count}")

# ==========================================================
# IPA SYLLABLE ANALYSIS
# ==========================================================

syllable_counter = Counter()

for ipa in errors["IPA"]:

    ipa = (
        str(ipa)
        .replace("/", "")
        .replace("ˈ", "")
        .replace("ˌ", "")
    )

    syllables = ipa.split(".")

    for syllable in syllables:

        syllable_counter[syllable] += 1

print("\n=== MOST COMMON PROBLEMATIC IPA SYLLABLES ===")

for syllable, count in syllable_counter.most_common(20):

    print(f"{syllable:15} {count}")

# ==========================================================
# ERROR CATEGORY ANALYSIS
# ==========================================================

error_categories = Counter()

for ipa in errors["IPA"]:

    ipa = str(ipa)

    # Diphthongs
    if "eɪ" in ipa:
        error_categories["Diphthong eɪ"] += 1

    if "aɪ" in ipa:
        error_categories["Diphthong aɪ"] += 1

    if "ɔɪ" in ipa:
        error_categories["Diphthong ɔɪ"] += 1

    if "oʊ" in ipa:
        error_categories["Diphthong oʊ"] += 1

    # Schwa
    if "ə" in ipa:
        error_categories["Schwa ə"] += 1

    # Long vowels
    if "ː" in ipa:
        error_categories["Long vowels"] += 1

    # Affricates
    if "t͡ʃ" in ipa:
        error_categories["Affricate t͡ʃ"] += 1

    if "d͡ʒ" in ipa:
        error_categories["Affricate d͡ʒ"] += 1

    # English R
    if "ɹ" in ipa:
        error_categories["English r (ɹ)"] += 1

    # French R
    if "ʁ" in ipa:
        error_categories["French r (ʁ)"] += 1

    # Nasals
    if "ŋ" in ipa:
        error_categories["Velar nasal ŋ"] += 1

    if "n" in ipa:
        error_categories["Final n"] += 1

print("\n=== ERROR CATEGORIES ===")

for category, count in error_categories.most_common():

    print(f"{category:25} {count}")

# ==========================================================
# RULES TO IMPROVE
# ==========================================================

print("\n=== RECOMMENDED RULES TO REVIEW ===")

for category, count in error_categories.most_common():

    if count >= 1:

        print(f"• {category}")

# ==========================================================
# CONCLUSION
# ==========================================================

print("\n=== SUMMARY ===")

print(
    "The majority of low-scoring translations involve "
    "complex vowel sounds, diphthongs, schwa reduction, "
    "long vowels, and English/French-specific consonants."
)

print(
    "\nThese rules should be prioritized before conducting "
    "another evaluation round."
)

print("\nAnalysis complete.")