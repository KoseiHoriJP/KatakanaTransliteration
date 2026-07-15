import sys
import os
import pandas as pd
import json

from collections import defaultdict

# --------------------------------------------------
# PROJECT SETUP
# --------------------------------------------------

PROJECT_ROOT = "/Users/kos/Desktop/PBL5_Project"
sys.path.append(PROJECT_ROOT)

from Parsers.ipa_parser import ipa_parser
from Parsers.pronunciation_parser import parse_pronunciation

SUPPORTED_LANGUAGES = {
    "English",
    "American English",
    "British English",
    "French"
}

# --------------------------------------------------
# MAIN TRANSLATION FUNCTION
# --------------------------------------------------

def generate_katakana_entry(name, language, ipa_string, pron_string):
    # 1. Parse Pronunciation
    pron_data = parse_pronunciation(pron_string)
    pron_syllables = pron_data["syllables"] 
    
    # 2. Clean IPA (Strips the dataset's specific apostrophes!)
    clean_ipa = (
        ipa_string
        .replace("/", "")
        .replace("ˈ", "") 
        .replace("ˌ", "") 
        .replace("'", "") 
        .replace(",", "") 
    )
    ipa_syllables = clean_ipa.split(".")
    
    raw_katakana = ""
    hybrid_katakana = ""
    aligned_hybrid_array = []

    # 3. Direct Alignment 
    if len(ipa_syllables) == len(pron_syllables):
        paired_syllables = list(zip(ipa_syllables, pron_syllables))
    else:
        paired_syllables = list(zip(ipa_syllables, ipa_syllables)) 

    # 4. Generate Katakana utilizing BOTH inputs
    for ipa_syll, pron_syll in paired_syllables:
        # Check if the English text is capitalized to trigger the long vowel
        is_stressed = pron_syll.isupper() and len(pron_syll) > 1 
        
        parsed = ipa_parser(
            ipa=ipa_syll,                
            language=language,
            pron_hint=pron_syll.lower(), 
            is_stressed=is_stressed      
        )
        
        kata = parsed["katakana_string"]
        
        if parsed.get("unmatched"):
            print(f"[UNMATCHED] {name} | {ipa_syll} -> {parsed['unmatched']}")

        raw_katakana += kata
        aligned_hybrid_array.append(kata)

    hybrid_katakana = "".join(aligned_hybrid_array)

    return {
        "name": name,
        "language": language,
        "ipa_original": ipa_string,
        "pronunciation_original": pron_string,
        "analysis": {
            "ipa_array_raw": ipa_syllables,
            "pron_array_raw": pron_syllables,
            "stress_position": pron_data.get("stress_position", -1),
            "hybrid_array": aligned_hybrid_array
        },
        "outputs": {
            "raw_literal": raw_katakana, 
            "hybrid_standard": hybrid_katakana
        }
    }

# --------------------------------------------------
# DATASET PROCESSOR (Fixed to handle multiple files)
# --------------------------------------------------

def process_datasets(input_csv_paths, output_json_path):
    print(f"Loading and merging {len(input_csv_paths)} datasets...")

    all_dataframes = []
    
    # Read each path safely and collect them into a list
    for path in input_csv_paths:
        if os.path.exists(path):
            print(f" -> Found: {os.path.basename(path)}")
            df = pd.read_csv(path)
            all_dataframes.append(df)
        else:
            print(f" -> [WARNING] Missing file at: {path}")

    if not all_dataframes:
        print("[ERROR] No valid CSV datasets found.")
        return

    # Combine the files together into one layout
    master_df = pd.concat(all_dataframes, ignore_index=True)

    # Clean missing values and drop exact name/lang duplicates
    initial_count = len(master_df)
    master_df = master_df.dropna(subset=["IPA", "Pronunciation_Text"])
    master_df = master_df.drop_duplicates(subset=["Name", "Language", "IPA"])
    
    total = len(master_df)
    print(f"\nMerged dataset ready. Unique entries to parse: {total} (Dropped {initial_count - total} duplicates/nulls)")
    print("-" * 50)

    results = []
    skipped = 0

    # Main iteration sequence
    for idx, row in master_df.reset_index(drop=True).iterrows():
        language = str(row["Language"]).strip()

        if language not in SUPPORTED_LANGUAGES:
            skipped += 1
            continue

        first_pron = str(row["Pronunciation_Text"]).split(",")[0].strip()

        try:
            entry = generate_katakana_entry(
                name=row["Name"],
                language=language,
                ipa_string=str(row["IPA"]),
                pron_string=first_pron
            )
            results.append(entry)
        except Exception as e:
            print(f"[ERROR] {row['Name']} ({language}): {e}")

        if (idx + 1) % 1000 == 0 or (idx + 1) == total:
            print(f"Processed {idx + 1}/{total}")

    # Save to your output path
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)

    print("-" * 50)
    print(f"Finished: {len(results)} valid names compiled")
    print(f"Skipped: {skipped} unsupported language rows")
    print(f"Saved directly to: {output_json_path}")

# --------------------------------------------------
# RUN PIPELINE
# --------------------------------------------------

if __name__ == "__main__":
    dataset_paths = [
        f"{PROJECT_ROOT}/Dataset/english_names_dataset.csv",
        f"{PROJECT_ROOT}/Dataset/french_names_dataset.csv"
    ]

    output_path = f"{PROJECT_ROOT}/Dataset/english_katakana_output2.json"

    print("Starting Multi-Language Pipeline...\n")
    process_datasets(dataset_paths, output_path)