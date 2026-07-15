# ipa_coverage.py

import pandas as pd
from collections import Counter

df = pd.read_csv("../Dataset/english_names_dataset.csv")

counter = Counter()

for ipa in df["IPA"].dropna():

    ipa = (
        str(ipa)
        .replace("/", "")
        .replace("ˈ", "")
        .replace("ˌ", "")
        .replace(".", "")
    )

    for ch in ipa:
        counter[ch] += 1

print("\n=== IPA SYMBOL FREQUENCY ===\n")

for symbol, count in counter.most_common():
    print(f"{symbol}: {count}")