import torch
import json
import time
from model import Encoder, Decoder, Seq2Seq 

def run_inference_only(input_text, model, input_char2index, target_index2char, device):
    """Stripped down inference function optimized purely for speed."""
    input_indexes = [input_char2index.get("<SOS>", 1)]
    for char in input_text:
        input_indexes.append(input_char2index.get(char, 3)) 
    input_indexes.append(input_char2index.get("<EOS>", 2))
    
    input_tensor = torch.tensor(input_indexes, dtype=torch.long, device=device).unsqueeze(0)

    # Start the high-precision timer
    start_time = time.perf_counter()

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

    # Stop the timer
    end_time = time.perf_counter()
    
    # Return both the prediction and the time it took (in milliseconds)
    latency_ms = (end_time - start_time) * 1000
    return "".join(decoded_chars), latency_ms

def benchmark_latency():
    MODEL_PATH = "katakana_model.pt"
    VOCAB_PATH = "../Dataset/training_vocab.json"
    DATASET_PATH = "../Dataset/english_katakana_output.json" 
    
    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    if torch.cuda.is_available(): device = torch.device("cuda")

    with open(VOCAB_PATH, "r", encoding="utf-8") as f:
        vocab = json.load(f)
    input_char2index = vocab["source_char2idx"]
    target_index2char = {int(k): v for k, v in vocab["target_idx2char"].items()}

    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        raw_data = json.load(f)
        
    eval_data = [item for item in raw_data if "name" in item and "ipa_original" in item][:1000] # Test on 1000 samples

    checkpoint = torch.load(MODEL_PATH, map_location=device, weights_only=False)
    INPUT_DIM = len(input_char2index)
    OUTPUT_DIM = len(vocab["target_char2idx"])
    HID_DIM = 256 
    
    encoder = Encoder(INPUT_DIM, HID_DIM)
    decoder = Decoder(HID_DIM, OUTPUT_DIM)
    model = Seq2Seq(encoder, decoder, device).to(device)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()

    print(f"⚙️ Hardware detected: {device.type.upper()}")
    print("🔥 Running 50 warm-up sequences (memory allocation)...")
    
    warmup_sample = f"<NAME>Warmup<LANG>English<IPA>/wɔɹm.ʌp/"
    for _ in range(50):
        run_inference_only(warmup_sample, model, input_char2index, target_index2char, device)

    print(f"🚀 Benchmarking {len(eval_data)} names...")
    
    latencies = []

    for item in eval_data:
        name = item["name"]
        lang = item.get("language", "English")
        ipa = item["ipa_original"]
        
        smart_input = f"<NAME>{name}<LANG>{lang}<IPA>{ipa}"
        _, latency = run_inference_only(smart_input, model, input_char2index, target_index2char, device)
        latencies.append(latency)

    # Calculate statistics
    avg_latency = sum(latencies) / len(latencies)
    max_latency = max(latencies)
    min_latency = min(latencies)
    throughput = 1000 / avg_latency # How many sequences per second

    print("\n" + "=" * 50)
    print("⚡ LATENCY BENCHMARK REPORT")
    print("=" * 50)
    print(f"Average Inference Time : {avg_latency:.2f} ms")
    print(f"Fastest Sequence       : {min_latency:.2f} ms")
    print(f"Slowest Sequence       : {max_latency:.2f} ms")
    print(f"Throughput             : {throughput:.0f} translations / second")
    print("=" * 50)

if __name__ == "__main__":
    benchmark_latency()