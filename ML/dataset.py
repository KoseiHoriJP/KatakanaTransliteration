import json
import os
import torch
from torch.utils.data import Dataset, DataLoader
from torch.nn.utils.rnn import pad_sequence

# --------------------------------------------------
# 1. VOCABULARY ENGINE
# --------------------------------------------------
class CharacterVocabulary:
    def __init__(self):
        self.pad_idx = 0  
        self.sos_idx = 1  
        self.eos_idx = 2  
        self.unk_idx = 3  
        
        self.char2idx = {"<PAD>": 0, "<SOS>": 1, "<EOS>": 2, "<UNK>": 3}
        self.idx2char = {0: "<PAD>", 1: "<SOS>", 2: "<EOS>", 3: "<UNK>"}
        self.vocab_size = 4

    def add_text(self, text):
        for char in text:
            if char not in self.char2idx:
                self.char2idx[char] = self.vocab_size
                self.idx2char[self.vocab_size] = char
                self.vocab_size += 1

    def numericalize(self, text):
        numericalized = [self.sos_idx]
        for char in text:
            numericalized.append(self.char2idx.get(char, self.unk_idx))
        numericalized.append(self.eos_idx)
        return torch.tensor(numericalized, dtype=torch.long)

    def decode(self, token_indices):
        chars = []
        for idx in token_indices:
            idx_val = idx.item() if isinstance(idx, torch.Tensor) else idx
            if idx_val in [self.sos_idx, self.eos_idx, self.pad_idx]:
                continue
            chars.append(self.idx2char.get(idx_val, ""))
        return "".join(chars)

# --------------------------------------------------
# 2. PYTORCH CUSTOM DATASET (STRICT READ-ONLY)
# --------------------------------------------------
class KatakanaDataset(Dataset):
    def __init__(self, json_path):
        if not os.path.exists(json_path):
            raise FileNotFoundError(f"Could not locate the final dataset at: {json_path}")
            
        with open(json_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
            
        self.entries = [item for item in raw_data if item.get("is_polished")]
        
        self.src_vocab = CharacterVocabulary()  
        self.trg_vocab = CharacterVocabulary()  
        
        self._build_vocabularies()

    def _build_vocabularies(self):
        for entry in self.entries:
            # Join them on one line using f-strings
            smart_input = (
                f"<NAME>{entry['name']}"
                f"<LANG>{entry['language']}"
                f"<IPA>{entry['ipa_original']}"
            )
            
            self.src_vocab.add_text(smart_input)
            self.trg_vocab.add_text(entry["outputs"]["hybrid_standard"])

    def __len__(self):
        return len(self.entries)

    def __getitem__(self, idx):
        entry = self.entries[idx]
        
        # Ensure this matches exactly what was built in the vocab
        smart_input = (
            f"<NAME>{entry['name']}"
            f"<LANG>{entry['language']}"
            f"<IPA>{entry['ipa_original']}"
        )
        
        src_tensor = self.src_vocab.numericalize(smart_input)
        trg_tensor = self.trg_vocab.numericalize(entry["outputs"]["hybrid_standard"])
        
        return src_tensor, trg_tensor

    def save_vocabularies_to_separate_file(self, output_vocab_path):
        vocab_payload = {
            "source_char2idx": self.src_vocab.char2idx,
            "source_idx2char": self.src_vocab.idx2char,
            "target_char2idx": self.trg_vocab.char2idx,
            "target_idx2char": self.trg_vocab.idx2char
        }
        with open(output_vocab_path, "w", encoding="utf-8") as f:
            json.dump(vocab_payload, f, ensure_ascii=False, indent=4)
        print(f"💾 Isolated Vocabulary definitions saved separately to: {output_vocab_path}")

# --------------------------------------------------
# 3. DYNAMIC BATCH COLLATOR
# --------------------------------------------------
class PadCollate:
    def __init__(self, pad_idx=0):
        self.pad_idx = pad_idx

    def __call__(self, batch):
        src_sequences = [item[0] for item in batch]
        trg_sequences = [item[1] for item in batch]
        
        src_padded = pad_sequence(src_sequences, batch_first=True, padding_value=self.pad_idx)
        trg_padded = pad_sequence(trg_sequences, batch_first=True, padding_value=self.pad_idx)
        
        return src_padded, trg_padded

if __name__ == "__main__":
    INPUT_DATASET_PATH = "../Dataset/english_katakana_output.json"
    OUTPUT_VOCAB_PATH = "../Dataset/training_vocab.json"
    
    print("Running secure tokenization separation...")
    try:
        dataset = KatakanaDataset(INPUT_DATASET_PATH)
        print(f" -> Master Dataset read perfectly without modifications.")
        print(f" -> Total processed source records: {len(dataset)}")
        dataset.save_vocabularies_to_separate_file(OUTPUT_VOCAB_PATH)
        print("\n🎉 Verification complete. Your data file is perfectly safe.")
    except Exception as e:
        print(f"\n[❌] Separation process failed: {e}")