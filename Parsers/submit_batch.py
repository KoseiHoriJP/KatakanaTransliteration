import json
import os
from openai import OpenAI

# Initialize OpenAI client (automatically picks up OPENAI_API_KEY from environment)
client = OpenAI()

# Configuration Paths
INPUT_JSON_PATH = "../Dataset/english_katakana_output.json"  # Change path/name if mixing languages
BATCH_INPUT_PATH = "multilingual_batch_tasks.jsonl"

def prepare_and_submit_batch():
    # 1. Load your existing dataset
    if not os.path.exists(INPUT_JSON_PATH):
        print(f"Error: Could not find dataset at {INPUT_JSON_PATH}")
        return

    with open(INPUT_JSON_PATH, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    print(f"Loaded {len(dataset)} names. Constructing language-aware batch tasks...")

    # 2. Build the JSONL task file
    with open(BATCH_INPUT_PATH, "w", encoding="utf-8") as f:
        for idx, entry in enumerate(dataset):
            name = entry.get("name", "")
            
            # Dynamically detect language if specified in your dataset, otherwise default to English
            # Expects your JSON objects to optionally have a "language": "French" key-value pair
            lang = entry.get("language", "English") 
            
            # Construct a system prompt customized for that specific language's pronunciation rules
            system_instruction = (
                f"You are a native Japanese translator specializing in foreign loanwords. "
                f"Convert the given name into natural, fluid Katakana based strictly on its native {lang} "
                f"pronunciation rules and standard Japanese media/cultural conventions. Do not perform a literal "
                f"character-by-character swap; match real-world human pronunciation rhythms. "
                f"Output ONLY the Katakana characters, absolutely nothing else."
            )

            task = {
                "custom_id": f"task_{idx}",
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": {
                    "model": "gpt-4o-mini",
                    "temperature": 0.0,  # Zero temperature ensures consistent, deterministic translations
                    "max_tokens": 30,
                    "messages": [
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": f"Name: {name}"}
                    ]
                }
            }
            # Write line as a single-line JSON string
            f.write(json.dumps(task, ensure_ascii=False) + "\n")

    print(f"Batch file '{BATCH_INPUT_PATH}' generated successfully. Uploading to OpenAI servers...")

    # 3. Upload file to OpenAI Batch endpoint
    with open(BATCH_INPUT_PATH, "rb") as file_data:
        uploaded_file = client.files.create(
            file=file_data,
            purpose="batch"
        )

    # 4. Fire off the asynchronous processing job
    batch_job = client.batches.create(
        input_file_id=uploaded_file.id,
        endpoint="/v1/chat/completions",
        completion_window="24h"  # OpenAI processes this in the background (usually takes 5-15 mins)
    )

    print("\n==================================================")
    print("🎉 BATCH JOB SUCCESSFULLY CREATED!")
    print("==================================================")
    print(f"Batch Job ID: {batch_job.id}")
    print("👉 Copy and save this ID. You will need it to retrieve your data later.")
    print("==================================================")

    # Clean up local temporary file
    if os.path.exists(BATCH_INPUT_PATH):
        os.remove(BATCH_INPUT_PATH)

if __name__ == "__main__":
    prepare_and_submit_batch()