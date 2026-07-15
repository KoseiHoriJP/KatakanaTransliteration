import os
import torch
import json
import eng_to_ipa as p2i
from model import Encoder, Decoder, Seq2Seq 

def run_translation(input_text, model, input_char2index, target_index2char, device):
    """Helper function to translate a single string"""
    input_indexes = [input_char2index.get("<SOS>", 1)]
    for char in input_text:
        input_indexes.append(input_char2index.get(char, 3)) # 3 is <UNK>
    input_indexes.append(input_char2index.get("<EOS>", 2))
    
    input_tensor = torch.tensor(input_indexes, dtype=torch.long, device=device).unsqueeze(0)

    with torch.no_grad():
        encoder_outputs, encoder_hidden = model.encoder(input_tensor)
        decoder_hidden = encoder_hidden
        decoder_input = torch.tensor([[1]], device=device)
        
        decoded_chars = []
        last_predicted_id = -1 
        
        for _ in range(30):
            decoder_output, decoder_hidden, _ = model.decoder(decoder_input, decoder_hidden, encoder_outputs)
            
            top_value, top_index = decoder_output.topk(1)
            predicted_id = top_index.item()
            
            if predicted_id == 2: # <EOS>
                break
                
            if predicted_id > 3 and predicted_id != last_predicted_id: 
                decoded_chars.append(target_index2char.get(predicted_id, ""))
                last_predicted_id = predicted_id 
                
            decoder_input = torch.tensor([[predicted_id]], device=device)

    return "".join(decoded_chars)

def interactive_terminal():
    # 1. LOAD THE DATA AND MODEL
    MODEL_PATH = "katakana_model.pt"
    VOCAB_PATH = "../Dataset/training_vocab.json"
    DATASET_PATH = "../Dataset/english_katakana_output.json" 
    
    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    if torch.cuda.is_available(): device = torch.device("cuda")

    with open(VOCAB_PATH, "r", encoding="utf-8") as f:
        vocab = json.load(f)
        
    input_char2index = vocab["source_char2idx"]
    target_index2char = {int(k): v for k, v in vocab["target_idx2char"].items()}

    # 2. GROUP DATASET BY NAME
    # This creates a dictionary where each name holds a list of all its country variations
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        raw_data = json.load(f)
        
    name_db = {}
    for item in raw_data:
        name_key = item.get("name", "").lower()
        if not name_key: continue
        if name_key not in name_db:
            name_db[name_key] = []
        name_db[name_key].append(item)

    # 3. INITIALIZE MODEL
    checkpoint = torch.load(MODEL_PATH, map_location=device, weights_only=False)
    INPUT_DIM = len(input_char2index)
    OUTPUT_DIM = len(vocab["target_char2idx"])
    HID_DIM = 256 
    
    encoder = Encoder(INPUT_DIM, HID_DIM)
    decoder = Decoder(HID_DIM, OUTPUT_DIM)
    model = Seq2Seq(encoder, decoder, device).to(device)
    
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()

    print("🧠 Waking up the Neural Network...")
    print(f"📖 Indexed {len(name_db)} unique names with regional variations.")
    print("✅ Model loaded successfully.\n")
    print("=" * 60)
    print(" Type an English name for Multi-Region Analysis.")
    print(" Type 'quit' or 'exit' to stop.")
    print("=" * 60)

    # 4. THE INTERACTIVE LOOP
    while True:
        user_input = input("\n📝 Enter Name: ").strip()
        
        if user_input.lower() in ["quit", "exit"]: break
        if not user_input: continue
            
        name = user_input.capitalize()
        name_lower = user_input.lower()
        
        print("-" * 60)
        
        # --- PATH A: NAME EXISTS IN DATASET ---
        if name_lower in name_db:
            print(f"Comparing regions and methods:\n")
            entries = name_db[name_lower]
            
            for entry in entries:
                lang = entry.get("language", "American English")
                ipa = entry.get("ipa_original", "N/A")
                
                # Fetch the different generation methods from your JSON
                outputs = entry.get("outputs", {})
                raw_literal = outputs.get("raw_literal", "N/A")
                hybrid_standard = outputs.get("hybrid_standard", "N/A")
                
                # Get the Neural Network's prediction based on the exact same input
                smart_input = f"<NAME>{name}<LANG>{lang}<IPA>{ipa}"
                llm_prediction = run_translation(smart_input, model, input_char2index, target_index2char, device)
                
                print(f"🌍 {lang}")
                print(f"   ├─ 🗣️  IPA Dictionary   : {ipa}")
                print(f"   ├─ ⚙️  IPA-Based (Raw)  : {raw_literal}")
                print(f"   ├─ 🎯 Hybrid Standard  : {hybrid_standard}")
                print(f"   └─ 🧠 LLM Prediction   : {llm_prediction}\n")

        # --- PATH B: UNSEEN NAME (DYNAMIC FALLBACK) ---
        else:
            print(f"⚠️ '{name}' is unseen! Generating Multi-Region LLM predictions...\n")
            
            # Generate Base IPA
            raw_ipa = p2i.convert(name).replace("*", "")
            raw_ipa = raw_ipa.replace("ʤ", "d͡ʒ").replace("ʧ", "t͡ʃ")
            ipa_string = f"/{raw_ipa}/"
            
            print(f"🔍 Dynamic IPA: {ipa_string}\n")
            
            # Test the model's ability to adapt to different language tags!
            languages_to_test = ["American English", "British English", "French", "Spanish"]
            
            for lang in languages_to_test:
                smart_input = f"<NAME>{name}<LANG>{lang}<IPA>{ipa_string}"
                llm_prediction = run_translation(smart_input, model, input_char2index, target_index2char, device)
                
                print(f"🌍 {lang} Simulation")
                print(f"   └─ 🧠 LLM Prediction : {llm_prediction}")
            
        print("-" * 60)

if __name__ == "__main__":
    interactive_terminal()