import os
import numpy as np
import pickle
from PIL import Image, ImageChops, ImageEnhance
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.utils import to_categorical
from sklearn.model_selection import train_test_split

IMAGE_SIZE = (128, 128)
DATA_DIR = "training"

def ela_image(path, quality=90):
    original = Image.open(path).convert("RGB")
    resaved_path = path + "_resaved.jpg"
    original.save(resaved_path, "JPEG", quality=quality)

    resaved = Image.open(resaved_path)
    ela = ImageChops.difference(original, resaved)

    extrema = ela.getextrema()
    max_diff = max(e[1] for e in extrema) or 1
    scale = 255.0 / max_diff

    ela = ImageEnhance.Brightness(ela).enhance(scale)
    ela = ela.resize(IMAGE_SIZE)

    return np.asarray(ela) / 255.0


X = []
y = []

for label, folder in enumerate(["tampered", "authentic"]):
    folder_path = os.path.join(DATA_DIR, folder)
    for img_name in os.listdir(folder_path):
        try:
            img_path = os.path.join(folder_path, img_name)
            X.append(ela_image(img_path))
            y.append(label)
        except:
            pass

X = np.array(X)
y = to_categorical(y, num_classes=2)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = Sequential([
    Conv2D(32, (3,3), activation="relu", input_shape=(128,128,3)),
    MaxPooling2D(2,2),

    Conv2D(64, (3,3), activation="relu"),
    MaxPooling2D(2,2),

    Flatten(),
    Dense(128, activation="relu"),
    Dropout(0.5),
    Dense(2, activation="softmax")
])

model.compile(
    optimizer="adam",
    loss="categorical_crossentropy",
    metrics=["accuracy"]
)

model.summary()

model.fit(
    X_train,
    y_train,
    epochs=10,
    batch_size=16,
    validation_data=(X_test, y_test)
)

os.makedirs("model", exist_ok=True)
with open("model/model_pickle.pkl", "wb") as f:
    pickle.dump(model, f)

print("✅ Model saved as model/model_pickle.pkl")
