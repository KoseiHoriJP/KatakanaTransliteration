import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, random_split

from dataset import KatakanaDataset, PadCollate
from model import Encoder, Decoder, Seq2Seq

def evaluate(model, dataloader, criterion, device):
    model.eval()
    total_loss = 0.0

    with torch.no_grad():
        for src, trg in dataloader:
            src = src.to(device)
            trg = trg.to(device)

            output = model(src, trg, teacher_forcing_ratio=0)

            output_dim = output.shape[-1]

            output = output[:, 1:].reshape(-1, output_dim)
            trg = trg[:, 1:].reshape(-1)

            loss = criterion(output, trg)
            total_loss += loss.item()

    return total_loss / len(dataloader)

def train_model():
    # --------------------------------------------------
    # DEVICE
    # --------------------------------------------------
    if torch.cuda.is_available():
        device = torch.device("cuda")
    elif torch.backends.mps.is_available():
        device = torch.device("mps")
    else:
        device = torch.device("cpu")

    print(f"🔥 Training on: {device}")

    # --------------------------------------------------
    # CONFIG
    # --------------------------------------------------
    DATA_PATH = "../Dataset/english_katakana_output.json"
    MODEL_SAVE_PATH = "katakana_model.pt"

    BATCH_SIZE = 64
    HIDDEN_SIZE = 256
    LEARNING_RATE = 0.001
    EPOCHS = 50
    patience = 5

    # --------------------------------------------------
    # LOAD DATASET
    # --------------------------------------------------
    print("📂 Loading dataset...")

    dataset = KatakanaDataset(DATA_PATH)

    train_size = int(0.9 * len(dataset))
    val_size = len(dataset) - train_size

    train_dataset, val_dataset = random_split(
        dataset,
        [train_size, val_size]
    )

    train_loader = DataLoader(
        train_dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
        collate_fn=PadCollate(
            pad_idx=dataset.src_vocab.pad_idx
        )
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
        collate_fn=PadCollate(
            pad_idx=dataset.src_vocab.pad_idx
        )
    )

    print(f"Training Samples: {len(train_dataset)}")
    print(f"Validation Samples: {len(val_dataset)}")

    # --------------------------------------------------
    # BUILD MODEL
    # --------------------------------------------------
    encoder = Encoder(
        dataset.src_vocab.vocab_size,
        HIDDEN_SIZE
    )

    decoder = Decoder(
        HIDDEN_SIZE,
        dataset.trg_vocab.vocab_size
    )

    model = Seq2Seq(
        encoder,
        decoder,
        device
    ).to(device)

    optimizer = optim.Adam(
        model.parameters(),
        lr=LEARNING_RATE
    )

    criterion = nn.CrossEntropyLoss(
        ignore_index=dataset.trg_vocab.pad_idx
    )

    # --------------------------------------------------
    # TRAINING LOOP
    # --------------------------------------------------
    best_val_loss = float("inf")

    print("\n🚀 Starting training...\n")

    for epoch in range(EPOCHS):
        model.train()
        total_train_loss = 0.0

        for src, trg in train_loader:
            src = src.to(device)
            trg = trg.to(device)

            optimizer.zero_grad()

            output = model(src, trg)

            output_dim = output.shape[-1]

            output = output[:, 1:].reshape(
                -1,
                output_dim
            )

            trg = trg[:, 1:].reshape(-1)

            loss = criterion(output, trg)

            loss.backward()

            torch.nn.utils.clip_grad_norm_(
                model.parameters(),
                max_norm=1.0
            )

            optimizer.step()

            total_train_loss += loss.item()

        train_loss = total_train_loss / len(train_loader)

        val_loss = evaluate(
            model,
            val_loader,
            criterion,
            device
        )

        print(
            f"Epoch [{epoch + 1}/{EPOCHS}] "
            f"| Train Loss: {train_loss:.4f} "
            f"| Val Loss: {val_loss:.4f}"
        )

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            torch.save(
                {
                    "model_state_dict": model.state_dict(),
                    "hidden_size": HIDDEN_SIZE,
                    "learning_rate": LEARNING_RATE,
                    "epochs": EPOCHS,
                    "best_val_loss": best_val_loss,
                    "src_vocab_size": dataset.src_vocab.vocab_size,
                    "trg_vocab_size": dataset.trg_vocab.vocab_size,
                },
                MODEL_SAVE_PATH
            )
            print(
                f"💾 Best model saved "
                f"(Val Loss: {best_val_loss:.4f})"
            )

    print("\n🎉 Training complete!")
    print(f"Best Validation Loss: {best_val_loss:.4f}")
    print(f"Saved to: {MODEL_SAVE_PATH}")

if __name__ == "__main__":
    train_model()