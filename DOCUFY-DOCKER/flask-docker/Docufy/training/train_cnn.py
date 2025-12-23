# ================== IMPORTS ==================
import os
import cv2
import numpy as np
from sklearn.model_selection import train_test_split

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.optimizers import Adam

# ================== PATHS ==================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = BASE_DIR
MODEL_DIR = os.path.join(BASE_DIR, "..", "model")
MODEL_PATH = os.path.join(MODEL_DIR, "ela_model.keras")

AUTHENTIC_DIR = os.path.join(DATASET_DIR, "authentic")
TAMPERED_DIR = os.path.join(DATASET_DIR, "tampered")

os.makedirs(MODEL_DIR, exist_ok=True)

IMG_SIZE = 128

# ================== LOAD DATA ==================
X = []
y = []

def load_images(folder, label):
    for img_name in os.listdir(folder):
        img_path = os.path.join(folder, img_name)
        try:
            img = cv2.imread(img_path)
            img = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
            img = img / 255.0
            X.append(img)
            y.append(label)
        except Exception as e:
            print(f"Skipping {img_path}: {e}")

load_images(AUTHENTIC_DIR, 1)   # Authentic = 1
load_images(TAMPERED_DIR, 0)    # Tampered = 0

X = np.array(X, dtype="float32")
y = np.array(y)

print(f"✅ Dataset loaded: {len(X)} images")

# ================== SPLIT DATA ==================
X_train, X_val, y_train, y_val = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ================== CNN MODEL ==================
model = Sequential([
    Conv2D(32, (3,3), activation="relu", input_shape=(IMG_SIZE, IMG_SIZE, 3)),
    MaxPooling2D(2,2),

    Conv2D(64, (3,3), activation="relu"),
    MaxPooling2D(2,2),

    Flatten(),
    Dense(128, activation="relu"),
    Dropout(0.5),
    Dense(2, activation="softmax")
])

model.compile(
    optimizer=Adam(learning_rate=0.0001),
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)

model.summary()

# ================== TRAIN ==================
model.fit(
    X_train, y_train,
    validation_data=(X_val, y_val),
    epochs=10,
    batch_size=8
)

# ================== SAVE MODEL (CORRECT WAY) ==================
model.save(MODEL_PATH)
print(f"\n✅ MODEL SAVED AT: {MODEL_PATH}")
