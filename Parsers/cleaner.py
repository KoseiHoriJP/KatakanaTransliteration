import json
import re

# Standard Full-Width Katakana unicode block
KATAKANA_REGEX = re.compile(r'^[\u30A0-\u30FF]+$')
INPUT_JSON_PATH = "../Dataset/english_katakana_output.json"

def active_wipe():
    print("🧹 Wiping the 157 corrupted entries...")
    with open(INPUT_JSON_PATH, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    wiped_count = 0

    for entry in dataset:
        if entry.get("is_polished"):
            katakana_text = entry["outputs"].get("hybrid_standard", "")
            
            if not KATAKANA_REGEX.match(katakana_text):
                # Reset the entry for Groq
                entry["is_polished"] = False
                entry["outputs"]["hybrid_standard"] = ""
                wiped_count += 1

    if wiped_count > 0:
        # Save the file with the resets
        with open(INPUT_JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(dataset, f, ensure_ascii=False, indent=4)
        print(f"✅ Successfully wiped {wiped_count} entries.")
        print("Master JSON saved. You are clear to run Groq.")

if __name__ == "__main__":
    active_wipe()