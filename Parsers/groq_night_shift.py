import json
import os
import time

try:
    from groq import Groq
except ImportError:
    print("[!] 'groq' library not installed. Run 'pip install groq' first.")
    exit(1)

client = Groq()

INPUT_JSON_PATH = "../Dataset/english_katakana_output.json"
MODEL_NAME = "llama-3.3-70b-versatile"  
MAX_NAME_RETRIES = 3  

def run_groq_night_shift():
    if not os.path.exists(INPUT_JSON_PATH):
        print(f"Error: Could not find dataset at {INPUT_JSON_PATH}")
        return

    print(f"Reading dataset from: {INPUT_JSON_PATH}")
    with open(INPUT_JSON_PATH, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    # NO BUGGY SELF-HEALING ENGINE. 
    # Just directly filter out items that are already polished.
    unpolished_items = [(idx, entry) for idx, entry in enumerate(dataset) if not entry.get("is_polished")]
    total_to_process = len(unpolished_items)
    
    print(f"Loaded dataset. {total_to_process} names remaining out of {len(dataset)} total.")
    print("Booting Strict Groq High-Speed Night Shift Engine...\n")

    if total_to_process == 0:
        print("🎉 All names are already polished!")
        return

    for count, (idx, entry) in enumerate(unpolished_items, 1):
        name = entry.get("name", "Unknown")
        lang = entry.get("language", "English")
        pronunciation = entry.get("pronunciation_original", "")

        system_instruction = (
            f"You are a native Japanese translator specializing in foreign names. "
            f"Convert the {lang} name '{name}' (pronounced roughly like '{pronunciation}') "
            f"into actual, standard Japanese Katakana characters. "
            f"CRITICAL RULE: You must use actual Japanese Katakana blocks (like ア, ブ, ラ). "
            f"Do NOT output English letters. Do NOT output Romaji text. "
            f"Output ONLY the raw Katakana script, absolutely nothing else."
        )

        success = False
        attempt = 0
        
        while not success and attempt < MAX_NAME_RETRIES:
            try:
                completion = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": f"Name: {name}"}
                    ],
                    temperature=0.0,
                    max_tokens=20
                )

                katakana_out = completion.choices[0].message.content.strip()
                
                if not katakana_out:
                    print(f"\n[!] Groq returned a blank response for '{name}'. Skipping...")
                    dataset[idx]["is_polished"] = True
                    success = True
                    break

                dataset[idx]["outputs"]["hybrid_standard"] = katakana_out
                dataset[idx]["is_polished"] = True

                print(f"[{count}/{total_to_process}] {name} ({lang}) -> {katakana_out}")

                if count % 20 == 0:
                    with open(INPUT_JSON_PATH, "w", encoding="utf-8") as f:
                        json.dump(dataset, f, ensure_ascii=False, indent=4)
                    print("💾 Checkpoint securely backed up to disk.")

                success = True
                time.sleep(2.1)  

            except Exception as e:
                attempt += 1
                print(f"\n[!] Network error on attempt {attempt}/{MAX_NAME_RETRIES}: {e}")
                time.sleep(5)

        if not success:
            print(f"\n[❌] Skipping '{name}' after max retries.")
            dataset[idx]["is_polished"] = True
            time.sleep(1)

    with open(INPUT_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False, indent=4)

    print("\n🎉 Success! Your dataset is fully updated with pure Japanese script.")

if __name__ == "__main__":
    run_groq_night_shift()