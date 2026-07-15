import json
import os
from openai import OpenAI

client = OpenAI()

# ⚠️ PASTE YOUR COPIED BATCH JOB ID HERE
BATCH_JOB_ID = "YOUR_BATCH_JOB_ID_HERE" 

INPUT_JSON_PATH = "../Dataset/english_katakana_output.json"
OUTPUT_JSON_PATH = "../Dataset/english_katakana_output.json"  # Overwrites with clean data safely

def fetch_and_merge_results():
    if BATCH_JOB_ID == "YOUR_BATCH_JOB_ID_HERE":
        print("Error: Please paste your real OpenAI Batch Job ID into the script first.")
        return

    print(f"Checking status for Batch Job: {BATCH_JOB_ID}...")
    job = client.batches.retrieve(BATCH_JOB_ID)
    print(f"Current Job Status: {job.status}")

    if job.status == "completed":
        print("Job complete! Downloading output content from servers...")
        
        # 1. Fetch text content from OpenAI storage
        file_response = client.files.content(job.output_file_id)
        results_text = file_response.text
        
        # 2. Map indices to their corresponding clean LLM translations
        llm_translations = {}
        for line in results_text.strip().split("\n"):
            if not line:
                continue
            res_json = json.loads(line)
            
            # Extract index from custom_id (e.g., "task_42" -> 42)
            idx = int(res_json["custom_id"].split("_")[1])
            katakana_out = res_json["response"]["body"]["choices"][0]["message"]["content"].strip()
            llm_translations[idx] = katakana_out

        # 3. Read original dataset file
        with open(INPUT_JSON_PATH, "r", encoding="utf-8") as f:
            dataset = json.load(f)

        # 4. Splice the fluid Katakana into your dataset structure
        updated_count = 0
        for idx, entry in enumerate(dataset):
            if idx in llm_translations:
                # Replaces the stiff rule-generated string with native human-sounding Katakana
                entry["katakana_string"] = llm_translations[idx]
                updated_count += 1

        # 5. Write back to disk
        with open(OUTPUT_JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(dataset, f, ensure_ascii=False, indent=4)

        print(f"Success! Merged {updated_count} fluid, language-adapted translations into your dataset.")
        print(f"Updated file saved to: {OUTPUT_JSON_PATH}")

    elif job.status == "failed":
        print("The batch job failed on OpenAI's infrastructure. Check your developer dashboard log.")
    else:
        print("The job is still in progress. Please wait a few more minutes and re-run this script.")

if __name__ == "__main__":
    fetch_and_merge_results()