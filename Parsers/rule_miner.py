import json
from collections import defaultdict
import re

DATA_PATH = "../Dataset/english_katakana_output.json"

def clean_ipa(ipa_string):
    """Removes slashes, syllable dots, and stress marks to get pure sound."""
    if not ipa_string:
        return ""
    # Remove /, ., ˈ, ˌ, and spaces
    return re.sub(r'[/\.ˈˌ ]', '', ipa_string)

def mine_phonetic_rules():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    # Dictionary to count: { "IPA_suffix": { "Katakana_suffix": count } }
    suffix_mappings = defaultdict(lambda: defaultdict(int))

    for entry in dataset:
        if not entry.get("is_polished"):
            continue
            
        ipa = clean_ipa(entry.get("ipa_original", ""))
        katakana = entry["outputs"].get("hybrid_standard", "")

        # We need names long enough to grab suffixes
        if len(ipa) >= 3 and len(katakana) >= 2:
            # Grab the last 3 IPA characters (e.g., 'ʃən' for 'tion')
            ipa_suffix = ipa[-3:]
            # Grab the last 2 Katakana characters (e.g., 'ション')
            kata_suffix = katakana[-2:]
            
            suffix_mappings[ipa_suffix][kata_suffix] += 1

    # --------------------------------------------------
    # DISPLAY THE GOLDEN RULES
    # --------------------------------------------------
    print("🌟 TOP PHONETIC RULES DISCOVERED 🌟\n")
    
    # Sort IPA suffixes by how often they appear
    sorted_ipas = sorted(suffix_mappings.items(), key=lambda x: sum(x[1].values()), reverse=True)

    for ipa_suff, kata_counts in sorted_ipas[:20]: # Show the top 20 most common
        total_occurrences = sum(kata_counts.values())
        
        # Find the most common Katakana translation for this IPA
        best_kata = max(kata_counts, key=kata_counts.get)
        best_count = kata_counts[best_kata]
        
        confidence = (best_count / total_occurrences) * 100
        
        # Only print rules that are highly reliable (over 90% confidence) and happen often
        if confidence >= 90.0 and total_occurrences > 15:
            print(f"IPA Suffix: '{ipa_suff}'")
            print(f" -> Translates to: '{best_kata}'")
            print(f" -> Confidence:    {confidence:.1f}% (Found in {best_count} names)")
            print("-" * 30)

if __name__ == "__main__":
    mine_phonetic_rules()