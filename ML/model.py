import torch
import torch.nn as nn
import torch.nn.functional as F
import random

# --------------------------------------------------
# 1. THE ENCODER (Reads input, returns output & hidden)
# --------------------------------------------------
class Encoder(nn.Module):
    def __init__(self, input_vocab_size, hidden_size):
        super(Encoder, self).__init__()
        self.embedding = nn.Embedding(input_vocab_size, hidden_size)
        self.gru = nn.GRU(hidden_size, hidden_size, batch_first=True)

    def forward(self, input_tensor):
        embedded = self.embedding(input_tensor)
        output, hidden = self.gru(embedded)
        return output, hidden

# --------------------------------------------------
# 2. THE ATTENTION DECODER (Translator with Flashlight)
# --------------------------------------------------
class Decoder(nn.Module):
    def __init__(self, hidden_size, output_vocab_size):
        super(Decoder, self).__init__()
        self.embedding = nn.Embedding(output_vocab_size, hidden_size)
        self.attn_combine = nn.Linear(hidden_size * 2, hidden_size)
        self.gru = nn.GRU(hidden_size, hidden_size, batch_first=True)
        self.out = nn.Linear(hidden_size, output_vocab_size)

    def forward(self, input_tensor, hidden, encoder_outputs):
        embedded = self.embedding(input_tensor)
        
        # Attention Calculation
        query = hidden.permute(1, 0, 2)
        keys = encoder_outputs.permute(0, 2, 1)
        attn_scores = torch.bmm(query, keys)
        attn_weights = F.softmax(attn_scores, dim=2) 
        context = torch.bmm(attn_weights, encoder_outputs)
        
        combined = torch.cat((embedded, context), dim=2)
        combined = self.attn_combine(combined)
        combined = F.relu(combined)
        
        output, hidden = self.gru(combined, hidden)
        prediction = self.out(output)
        return prediction, hidden, attn_weights

# --------------------------------------------------
# 3. THE SEQ2SEQ MASTER WRAPPER (Wires them together)
# --------------------------------------------------
class Seq2Seq(nn.Module):
    def __init__(self, encoder, decoder, device):
        super(Seq2Seq, self).__init__()
        self.encoder = encoder
        self.decoder = decoder
        self.device = device

    def forward(self, src, trg, teacher_forcing_ratio=0.5):
        batch_size = src.shape[0]
        trg_len = trg.shape[1]
        trg_vocab_size = self.decoder.out.out_features

        # Create an empty matrix to hold the decoder's Katakana predictions
        outputs = torch.zeros(batch_size, trg_len, trg_vocab_size).to(self.device)

        # 1. Pass the entire English name batch into the Encoder
        encoder_outputs, hidden = self.encoder(src)

        # 2. Grab the <SOS> token (Index 1) to feed as the first input to Decoder
        decoder_input = trg[:, 0].unsqueeze(1) 

        # 3. Loop character-by-character through the target length
        for t in range(1, trg_len):
            
            # Predict the next Katakana character
            prediction, hidden, attn_weights = self.decoder(decoder_input, hidden, encoder_outputs)
            
            # Save the prediction in our outputs matrix
            outputs[:, t, :] = prediction.squeeze(1)
            
            # Find the index of the character with the highest probability (The AI's guess)
            top1 = prediction.argmax(dim=2)
            
            # TEACHER FORCING: Roll a dice. 
            # If we land under the ratio, use the real correct target character next.
            # Otherwise, use the model's own guess.
            teacher_force = random.random() < teacher_forcing_ratio
            decoder_input = trg[:, t].unsqueeze(1) if teacher_force else top1

        return outputs