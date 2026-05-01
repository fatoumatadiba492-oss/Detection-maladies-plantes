"""
Script d'entraînement — Détection des maladies des plantes
Modèle   : EfficientNet-B4 (transfer learning depuis ImageNet)
Dataset  : PlantVillage (38 classes, ~87 000 images)
Résultat : model/plant_disease_efficientnet.pt

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PRÉPARATION DU DATASET
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Télécharger PlantVillage depuis Kaggle :
   kaggle datasets download -d abdallahalidev/plantvillage-dataset

2. Dézipper dans : backend/dataset/PlantVillage/
   Structure attendue :
   dataset/PlantVillage/
   ├── Apple___Apple_scab/
   │   ├── image001.JPG
   │   └── ...
   ├── Apple___Black_rot/
   └── ... (38 dossiers)

3. Lancer l'entraînement :
   cd backend
   python train_model.py

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DURÉE ESTIMÉE (selon matériel)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
GPU NVIDIA RTX 3060 : ~25 min / epoch, ~12h total
CPU seulement       : ~3h / epoch (non recommandé)
Google Colab GPU    : ~30 min / epoch — RECOMMANDÉ
"""

import os
import json
import time
import copy

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, random_split, WeightedRandomSampler
from torchvision import datasets, transforms
from torchvision.models import efficientnet_b4, EfficientNet_B4_Weights

# ── Configuration ──────────────────────────────────────────────────────────────
DATA_DIR   = os.getenv('DATASET_PATH', 'dataset/PlantVillage')
MODEL_DIR  = 'model'
MODEL_OUT  = os.path.join(MODEL_DIR, 'plant_disease_efficientnet.pt')
EPOCHS     = 30
BATCH_SIZE = 32
LR         = 1e-4
VAL_SPLIT  = 0.15
IMG_SIZE   = 380       # EfficientNet-B4 taille native
DEVICE     = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
NUM_WORKERS = min(4, os.cpu_count() or 1) if torch.cuda.is_available() else 0
LABEL_SMOOTHING = 0.1
GRAD_CLIP  = 1.0

os.makedirs(MODEL_DIR, exist_ok=True)

print("=" * 60)
print("  PlantAI — Entraînement EfficientNet-B4")
print("=" * 60)
print(f"  Dispositif : {DEVICE}")
print(f"  Dataset    : {DATA_DIR}")
print(f"  Epochs     : {EPOCHS}")
print(f"  Batch      : {BATCH_SIZE}")
print(f"  Workers    : {NUM_WORKERS}")
print("=" * 60)

# ── Vérification du dataset ────────────────────────────────────────────────────
if not os.path.isdir(DATA_DIR):
    print(f"\n❌  Dataset introuvable : {DATA_DIR}")
    print("""
Téléchargez PlantVillage depuis Kaggle :
  pip install kaggle
  kaggle datasets download -d abdallahalidev/plantvillage-dataset
  unzip plantvillage-dataset.zip -d dataset/PlantVillage

Ou depuis TensorFlow Datasets :
  pip install tensorflow-datasets
  python -c "import tensorflow_datasets as tfds; tfds.load('plant_village')"
""")
    exit(1)

# ── Transforms ────────────────────────────────────────────────────────────────
train_tf = transforms.Compose([
    transforms.RandomResizedCrop(IMG_SIZE, scale=(0.65, 1.0)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomVerticalFlip(p=0.25),
    transforms.ColorJitter(brightness=0.35, contrast=0.35, saturation=0.35, hue=0.12),
    transforms.RandomRotation(30),
    transforms.RandomAffine(degrees=0, translate=(0.1, 0.1), shear=10),
    transforms.RandomGrayscale(p=0.05),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    transforms.RandomErasing(p=0.2, scale=(0.02, 0.1)),
])

val_tf = transforms.Compose([
    transforms.Resize(420),
    transforms.CenterCrop(IMG_SIZE),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
])

# ── Dataset ────────────────────────────────────────────────────────────────────
print("\n📂 Chargement du dataset…")
full_dataset = datasets.ImageFolder(DATA_DIR)
class_names  = full_dataset.classes
num_classes  = len(class_names)

print(f"  Classes     : {num_classes}")
print(f"  Images      : {len(full_dataset)}")
print(f"  Exemples    : {class_names[:3]} …")

# Sauvegarde des noms de classes
with open(os.path.join(MODEL_DIR, 'class_names.json'), 'w', encoding='utf-8') as f:
    json.dump({'classes': class_names, 'num_classes': num_classes,
               'class_to_idx': full_dataset.class_to_idx}, f, ensure_ascii=False, indent=2)

# Split train/val
n_val   = int(len(full_dataset) * VAL_SPLIT)
n_train = len(full_dataset) - n_val
train_ds, val_ds = random_split(
    full_dataset, [n_train, n_val],
    generator=torch.Generator().manual_seed(42)
)

# Weighted sampler pour classes déséquilibrées
class_counts = torch.tensor([0] * num_classes, dtype=torch.float)
for _, label in full_dataset:
    class_counts[label] += 1
weights_per_class = 1.0 / (class_counts + 1e-6)
sample_weights = [weights_per_class[full_dataset.targets[i]] for i in train_ds.indices]
sampler = WeightedRandomSampler(sample_weights, len(sample_weights))

# Appliquer les transforms
train_ds.dataset.transform = train_tf
val_ds.dataset.transform   = val_tf

train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, sampler=sampler,
                          num_workers=NUM_WORKERS, pin_memory=True)
val_loader   = DataLoader(val_ds,   batch_size=BATCH_SIZE, shuffle=False,
                          num_workers=NUM_WORKERS, pin_memory=True)

print(f"\n  Train : {n_train} images | Val : {n_val} images")

# ── Modèle ────────────────────────────────────────────────────────────────────
print("\n🧠 Construction du modèle EfficientNet-B4…")
model = efficientnet_b4(weights=EfficientNet_B4_Weights.IMAGENET1K_V1)

# Fine-tuning : geler les premières couches, libérer les dernières
for name, param in model.named_parameters():
    if 'features.7' in name or 'features.8' in name or 'classifier' in name:
        param.requires_grad = True
    else:
        param.requires_grad = False

# Remplacer le classifier
in_features = model.classifier[1].in_features
model.classifier = nn.Sequential(
    nn.Dropout(0.4),
    nn.Linear(in_features, 512),
    nn.ReLU(),
    nn.Dropout(0.3),
    nn.Linear(512, num_classes),
)
model = model.to(DEVICE)

trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
total     = sum(p.numel() for p in model.parameters())
print(f"  Paramètres entraînables : {trainable:,} / {total:,}")

# ── Loss & Optimizer ──────────────────────────────────────────────────────────
criterion = nn.CrossEntropyLoss(label_smoothing=LABEL_SMOOTHING)
optimizer = optim.AdamW(
    filter(lambda p: p.requires_grad, model.parameters()),
    lr=LR, weight_decay=1e-4
)
scheduler = optim.lr_scheduler.CosineAnnealingWarmRestarts(optimizer, T_0=10, T_mult=2)

# ── Boucle d'entraînement ─────────────────────────────────────────────────────
best_acc   = 0.0
best_state = None
history    = {'train_loss': [], 'val_loss': [], 'train_acc': [], 'val_acc': []}

print(f"\n🚀 Démarrage de l'entraînement ({EPOCHS} epochs)…\n")

for epoch in range(EPOCHS):
    t0 = time.time()

    # Phase 2 : déblocage progressif des couches inférieures
    if epoch == 10:
        print("🔓 Epoch 10 : déblocage des couches features.5 et supérieures")
        for name, param in model.named_parameters():
            if any(f'features.{i}' in name for i in range(5, 9)) or 'classifier' in name:
                param.requires_grad = True
        optimizer.add_param_group({'params': [p for n, p in model.named_parameters()
                                              if p.requires_grad and 'features.5' in n
                                              or 'features.6' in n], 'lr': LR * 0.1})

    for phase in ['train', 'val']:
        is_train = (phase == 'train')
        model.train() if is_train else model.eval()
        loader = train_loader if is_train else val_loader

        total_loss = total_correct = total_samples = 0

        with torch.set_grad_enabled(is_train):
            for imgs, labels in loader:
                imgs, labels = imgs.to(DEVICE), labels.to(DEVICE)
                optimizer.zero_grad(set_to_none=True)

                outputs = model(imgs)
                loss    = criterion(outputs, labels)

                if is_train:
                    loss.backward()
                    nn.utils.clip_grad_norm_(model.parameters(), GRAD_CLIP)
                    optimizer.step()

                preds          = outputs.argmax(dim=1)
                total_loss    += loss.item() * imgs.size(0)
                total_correct += (preds == labels).sum().item()
                total_samples += imgs.size(0)

        epoch_loss = total_loss / total_samples
        epoch_acc  = total_correct / total_samples

        history[f'{phase}_loss'].append(epoch_loss)
        history[f'{phase}_acc'].append(epoch_acc)

        if phase == 'val' and epoch_acc > best_acc:
            best_acc   = epoch_acc
            best_state = copy.deepcopy(model.state_dict())
            torch.save({
                'epoch':            epoch + 1,
                'model_state_dict': best_state,
                'class_names':      class_names,
                'num_classes':      num_classes,
                'accuracy':         best_acc,
                'history':          history,
            }, MODEL_OUT)
            flag = " ← ✅ MEILLEUR"
        else:
            flag = ""

        print(f"[{phase:5s}] Loss: {epoch_loss:.4f}  Acc: {epoch_acc:.4f}{flag}")

    scheduler.step()
    elapsed = time.time() - t0
    lr_now  = scheduler.get_last_lr()[0]
    print(f"Epoch {epoch+1:3d}/{EPOCHS}  LR: {lr_now:.2e}  Temps: {elapsed:.1f}s\n")

# ── Résultat final ─────────────────────────────────────────────────────────────
print("=" * 60)
print(f"  Entraînement terminé !")
print(f"  Meilleure précision validation : {best_acc*100:.2f}%")
print(f"  Modèle sauvegardé              : {MODEL_OUT}")
print("=" * 60)
print("""
Pour utiliser ce modèle :
  - Il est automatiquement détecté par model_logic.py au démarrage
  - Aucune modification nécessaire dans app.py
""")
