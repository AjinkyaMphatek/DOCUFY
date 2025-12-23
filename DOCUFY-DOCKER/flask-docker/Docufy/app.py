# # ================== IMPORTS ==================
# import os
# import io
# import base64
# import pickle
# import hashlib
# from datetime import timedelta
# from uuid import uuid4

# import numpy as np
# from numpy import array

# from flask import (
#     Flask, jsonify, render_template,
#     request, redirect, url_for,
#     session, flash
# )
# from flask_cors import CORS

# from PIL import Image, ImageChops, ImageEnhance

# from admin import Admin
# from database import Database
# from blockchain import Blockchain

# # ================== APP CONFIG ==================
# app = Flask(__name__)
# CORS(app)

# app.secret_key = "Docufy"
# app.permanent_session_lifetime = timedelta(minutes=10)

# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# STATIC_DIR = os.path.join(BASE_DIR, "static")
# UPLOAD_DIR = os.path.join(STATIC_DIR, "uploads")
# MODEL_PATH = os.path.join(BASE_DIR, "model", "model_pickle.pkl")

# os.makedirs(UPLOAD_DIR, exist_ok=True)

# blockchain = Blockchain()
# node_address = str(uuid4()).replace("-", "")

# # ================== LOAD CNN MODEL (PICKLE) ==================
# if not os.path.exists(MODEL_PATH):
#     raise FileNotFoundError(
#         f"❌ Model not found at {MODEL_PATH}. Run train_cnn.py first."
#     )

# with open(MODEL_PATH, "rb") as f:
#     ela_model = pickle.load(f)

# print("✅ CNN model loaded successfully")

# # ================== ROUTES ==================

# @app.route("/")
# @app.route("/index")
# def index():
#     return render_template("index.html")


# @app.route("/admin")
# def admin():
#     return render_template("adminLogin.html")


# @app.route("/register")
# def register():
#     return render_template("Register.html")


# @app.route("/logout")
# def admin_logout():
#     session.clear()
#     return redirect(url_for("admin"))

# # ================== AUTH ==================

# @app.route("/user/register", methods=["POST"])
# def user_register():
#     username = request.form["username"]
#     password = request.form["password"]

#     if Admin.getAdmin({"username": username}):
#         flash("User already exists", "danger")
#         return redirect(url_for("register"))

#     admin = Admin(username=username, password=password)
#     admin.addAdmin()

#     session["user"] = username
#     flash("Registration successful", "success")
#     return redirect(url_for("index"))


# @app.route("/admin/authenticate", methods=["POST"])
# def admin_authenticate():
#     username = request.form["username"]
#     password = request.form["password"]

#     admin = Admin.getAdmin({"username": username, "password": password})
#     if not admin:
#         flash("Invalid credentials", "danger")
#         return redirect(url_for("admin"))

#     session["admin"] = username
#     flash("Login successful", "success")
#     return redirect(url_for("index"))

# # ================== ISSUE DOCUMENT ==================

# @app.route("/issue")
# def issue():
#     return render_template("issue.html")


# @app.route("/minechain", methods=["POST"])
# def minechain():
#     data = request.json
#     image_base64 = data.get("image")

#     if not image_base64:
#         return jsonify({"error": "No image provided"}), 400

#     image_bytes = base64.b64decode(image_base64)
#     sha_signature = hashlib.sha256(image_bytes).hexdigest()

#     previous_block = blockchain.get_previous_block()
#     proof = blockchain.proof_of_work(previous_block["proof"])
#     previous_hash = blockchain.hash(previous_block)

#     blockchain.create_block(
#         proof=proof,
#         previous_hash=previous_hash,
#         sha_signature=sha_signature
#     )

#     return jsonify({
#         "message": "Document successfully added to blockchain",
#         "hash": sha_signature
#     })

# # ================== ERROR LEVEL ANALYSIS ==================

# @app.route("/analysis")
# def analysis():
#     return render_template("analysis.html")


# @app.route("/predict", methods=["POST"])
# def predict():
#     data = request.json
#     image_base64 = data.get("image")

#     if not image_base64:
#         return jsonify({"error": "No image received"}), 400

#     image_bytes = base64.b64decode(image_base64)
#     image_path = os.path.join(UPLOAD_DIR, f"{uuid4().hex}.jpg")

#     with open(image_path, "wb") as f:
#         f.write(image_bytes)

#     # -------- ELA PROCESS --------
#     im = Image.open(image_path).convert("RGB")
#     resaved_path = image_path.replace(".jpg", "_resaved.jpg")
#     im.save(resaved_path, "JPEG", quality=90)

#     ela_image = ImageChops.difference(im, Image.open(resaved_path))
#     extrema = ela_image.getextrema()
#     max_diff = max(e[1] for e in extrema) or 1
#     scale = 255.0 / max_diff

#     ela_image = ImageEnhance.Brightness(ela_image).enhance(scale)

#     ela_array = array(ela_image.resize((128, 128))) / 255.0
#     ela_array = ela_array.reshape(-1, 128, 128, 3)

#     prediction = ela_model.predict(ela_array, verbose=0).flatten()

#     if prediction[1] > 0.5:
#         result = "Image is Authentic"
#         score = round(prediction[1] * 100, 2)
#     else:
#         result = "Image is Tampered"
#         score = round(prediction[0] * 100, 2)

#     buffer = io.BytesIO()
#     ela_image.save(buffer, format="JPEG")
#     ela_base64 = base64.b64encode(buffer.getvalue()).decode()

#     return jsonify({
#         "result": result,
#         "score": score,
#         "ela_image": f"data:image/jpeg;base64,{ela_base64}"
#     })

# # ================== BLOCKCHAIN ==================

# @app.route("/get_chain")
# def get_chain():
#     return jsonify({
#         "chain": blockchain.chain,
#         "length": len(blockchain.chain)
#     })


# @app.route("/is_valid")
# def is_valid():
#     valid = blockchain.is_chain_valid(blockchain.chain)
#     return jsonify({
#         "message": "Blockchain valid" if valid else "Blockchain invalid"
#     })

# # ================== RUN ==================

# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5000, debug=True)

# ================== IMPORTS ==================
import os
import io
import base64
import hashlib
from datetime import timedelta
from uuid import uuid4

import numpy as np
from numpy import array

from flask import (
    Flask, jsonify, render_template,
    request, redirect, url_for,
    session, flash
)
from flask_cors import CORS

from PIL import Image, ImageChops, ImageEnhance
from tensorflow.keras.models import load_model

from admin import Admin
from database import Database
from blockchain import Blockchain

# ================== APP CONFIG ==================
app = Flask(__name__)
CORS(app)

app.secret_key = "Docufy"
app.permanent_session_lifetime = timedelta(minutes=10)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
UPLOAD_DIR = os.path.join(STATIC_DIR, "uploads")
MODEL_PATH = os.path.join(BASE_DIR, "model", "ela_model.keras")

os.makedirs(UPLOAD_DIR, exist_ok=True)

blockchain = Blockchain()
node_address = str(uuid4()).replace("-", "")

# ================== LOAD CNN MODEL ==================
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"❌ Model not found: {MODEL_PATH}")

ela_model = load_model(MODEL_PATH)
print("✅ CNN model loaded successfully")

# ================== ROUTES ==================

@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html")


@app.route("/analysis")
def analysis():
    return render_template("analysis.html")


# ================== PREDICTION ==================

@app.route("/predict", methods=["POST"])
def predict():
    data = request.json
    image_base64 = data.get("image")

    if not image_base64:
        return jsonify({"error": "No image received"}), 400

    # Decode image
    image_bytes = base64.b64decode(image_base64)
    image_path = os.path.join(UPLOAD_DIR, f"{uuid4().hex}.jpg")

    with open(image_path, "wb") as f:
        f.write(image_bytes)

    # ================== ELA PROCESS ==================
    im = Image.open(image_path).convert("RGB")

    resaved_path = image_path.replace(".jpg", "_resaved.jpg")
    im.save(resaved_path, "JPEG", quality=90)

    ela_image = ImageChops.difference(im, Image.open(resaved_path))

    extrema = ela_image.getextrema()
    max_diff = max(e[1] for e in extrema) or 1
    scale = 255.0 / max_diff

    ela_image = ImageEnhance.Brightness(ela_image).enhance(scale)

    # ================== CNN ==================
    ela_array = array(ela_image.resize((128, 128))) / 255.0
    ela_array = ela_array.reshape(-1, 128, 128, 3)

    prediction = ela_model.predict(ela_array, verbose=0).flatten()

    if prediction[1] > 0.5:
        result = "Image is Authentic"
        score = round(prediction[1] * 100, 2)
    else:
        result = "Image is Tampered"
        score = round(prediction[0] * 100, 2)

    # ================== RESPONSE ==================
    buffer = io.BytesIO()
    ela_image.save(buffer, format="JPEG")
    ela_base64 = base64.b64encode(buffer.getvalue()).decode()

    return jsonify({
        "result": result,
        "score": score,
        "ela_image": f"data:image/jpeg;base64,{ela_base64}"
    })


# ================== BLOCKCHAIN ==================

@app.route("/get_chain")
def get_chain():
    return jsonify({
        "chain": blockchain.chain,
        "length": len(blockchain.chain)
    })


@app.route("/is_valid")
def is_valid():
    valid = blockchain.is_chain_valid(blockchain.chain)
    return jsonify({
        "message": "Blockchain valid" if valid else "Blockchain invalid"
    })


# ================== RUN ==================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
