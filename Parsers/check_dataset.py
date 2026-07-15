import json
import os

# 1. Check if the file actually exists
file_path = "../Dataset/english_katakana_output.json"

if not os.path.exists(file_path):
    print(f"ERROR: Could not find the file at {os.path.abspath(file_path)}")
else:
    print(f"SUCCESS: Found file at {file_path}")
    
    # 2. Load the data
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    print(f"Processing {len(data)} entries...")

    # 3. Simple scan
    suspicious_count = 0
    for entry in data:
        # Check for typical "robotic" patterns
        katakana = entry.get('katakana_string', '')
        
        # Logic: Flag if it contains obviously broken patterns
        if "アア" in katakana or "イイ" in katakana or "ウウ" in katakana:
            print(f"Flagged: {entry.get('name')} -> {katakana}")
            suspicious_count += 1
    
    print(f"---")
    print(f"Scan complete. Found {suspicious_count} suspicious entries.")