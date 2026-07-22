"""
Entraînement — Modèle CNN Keras (MobileNetV2 transfer learning, ou CNN Sequential simple)
────────────────────────────────────────────────────────────────────────────────────────
Dataset attendu (dossiers par classe) :
  data/train/<classe>/*.jpg
  data/val/<classe>/*.jpg

Résultat :
  model/plant_disease_model.keras
  model/class_names.json

Lancer :
  cd ia
  pip install -r requirements.txt
  python train_model.py

Variables d'environnement optionnelles :
  DATASET_PATH   chemin du dossier data/ (défaut : "data")
  ARCHITECTURE   "mobilenet" (défaut, transfer learning) ou "simple" (CNN Sequential)
"""

import os
import json

import tensorflow as tf
from tensorflow.keras import layers, models

# ── Configuration ──────────────────────────────────────────────────────────────
DATA_DIR    = os.getenv('DATASET_PATH', 'data')
TRAIN_DIR   = os.path.join(DATA_DIR, 'train')
VAL_DIR     = os.path.join(DATA_DIR, 'val')

MODEL_DIR        = 'model'
MODEL_OUT        = os.path.join(MODEL_DIR, 'plant_disease_model.keras')
CLASS_NAMES_OUT  = os.path.join(MODEL_DIR, 'class_names.json')

IMG_SIZE     = 224
BATCH_SIZE   = 32
EPOCHS       = 15
ARCHITECTURE = os.getenv('ARCHITECTURE', 'mobilenet')  # 'mobilenet' ou 'simple'

os.makedirs(MODEL_DIR, exist_ok=True)

if not os.path.isdir(TRAIN_DIR) or not os.path.isdir(VAL_DIR):
    raise SystemExit(
        "Dataset introuvable. Structure attendue :\n"
        f"  {TRAIN_DIR}/<classe>/*.jpg\n"
        f"  {VAL_DIR}/<classe>/*.jpg"
    )

print("=" * 60)
print("  PlantAI — Entraînement CNN Keras")
print(f"  Architecture : {ARCHITECTURE}")
print(f"  Dataset      : {DATA_DIR}")
print("=" * 60)

# ── Chargement du dataset ──────────────────────────────────────────────────────
train_ds = tf.keras.utils.image_dataset_from_directory(
    TRAIN_DIR, image_size=(IMG_SIZE, IMG_SIZE), batch_size=BATCH_SIZE,
)
val_ds = tf.keras.utils.image_dataset_from_directory(
    VAL_DIR, image_size=(IMG_SIZE, IMG_SIZE), batch_size=BATCH_SIZE,
)

class_names = train_ds.class_names
num_classes = len(class_names)
print(f"\nClasses détectées ({num_classes}) : {class_names}\n")

with open(CLASS_NAMES_OUT, 'w', encoding='utf-8') as f:
    json.dump({'classes': class_names, 'num_classes': num_classes}, f, ensure_ascii=False, indent=2)

AUTOTUNE = tf.data.AUTOTUNE
train_ds = train_ds.cache().shuffle(1000).prefetch(buffer_size=AUTOTUNE)
val_ds   = val_ds.cache().prefetch(buffer_size=AUTOTUNE)

data_augmentation = models.Sequential([
    layers.RandomFlip('horizontal'),
    layers.RandomRotation(0.1),
    layers.RandomZoom(0.1),
])

# ── Construction du modèle ──────────────────────────────────────────────────────
if ARCHITECTURE == 'mobilenet':
    base_model = tf.keras.applications.MobileNetV2(
        input_shape=(IMG_SIZE, IMG_SIZE, 3), include_top=False, weights='imagenet',
    )
    base_model.trainable = False

    inputs = tf.keras.Input(shape=(IMG_SIZE, IMG_SIZE, 3))
    x = data_augmentation(inputs)
    x = tf.keras.applications.mobilenet_v2.preprocess_input(x)
    x = base_model(x, training=False)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dropout(0.3)(x)
    outputs = layers.Dense(num_classes, activation='softmax')(x)
    model = models.Model(inputs, outputs)
else:
    model = models.Sequential([
        layers.Input(shape=(IMG_SIZE, IMG_SIZE, 3)),
        data_augmentation,
        layers.Rescaling(1. / 255),
        layers.Conv2D(32, 3, activation='relu'), layers.MaxPooling2D(),
        layers.Conv2D(64, 3, activation='relu'), layers.MaxPooling2D(),
        layers.Conv2D(128, 3, activation='relu'), layers.MaxPooling2D(),
        layers.Flatten(),
        layers.Dense(128, activation='relu'),
        layers.Dropout(0.4),
        layers.Dense(num_classes, activation='softmax'),
    ])

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=1e-4),
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy'],
)
model.summary()

# ── Entraînement ────────────────────────────────────────────────────────────────
callbacks = [
    tf.keras.callbacks.ModelCheckpoint(MODEL_OUT, save_best_only=True, monitor='val_accuracy', mode='max'),
    tf.keras.callbacks.EarlyStopping(monitor='val_accuracy', patience=5, restore_best_weights=True),
]

print(f"\nDémarrage de l'entraînement ({EPOCHS} epochs max, arrêt anticipé possible)…\n")
history = model.fit(train_ds, validation_data=val_ds, epochs=EPOCHS, callbacks=callbacks)

best_val_acc = max(history.history['val_accuracy'])
print("\n" + "=" * 60)
print(f"  Entraînement terminé — meilleure précision validation : {best_val_acc * 100:.2f}%")
print(f"  Modèle sauvegardé   : {MODEL_OUT}")
print(f"  Classes sauvegardées: {CLASS_NAMES_OUT}")
print("=" * 60)
