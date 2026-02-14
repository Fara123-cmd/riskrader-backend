from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import pickle
import numpy as np

# OPTIONAL IMPORTS (SAFE)
try:
    import xgboost as xgb
except ImportError:
    xgb = None

from crowd_density import crowd_density, crowd_alert
from firebase_service import send_alert

# -------------------------
# APP SETUP
# -------------------------
app = Flask(__name__)
CORS(app)

# -------------------------
# BASE DIRECTORY (RENDER SAFE)
# -------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# -------------------------
# LOAD MODEL FILES SAFELY
# -------------------------
model = None
scaler = None
features = []

try:
    if xgb is None:
        raise ImportError("xgboost not installed")

    model = xgb.XGBClassifier()
    model.load_model(os.path.join(BASE_DIR, "crime_model.json"))

    with open(os.path.join(BASE_DIR, "scaler.pkl"), "rb") as f:
        scaler = pickle.load(f)

    with open(os.path.join(BASE_DIR, "features.pkl"), "rb") as f:
        features = pickle.load(f)

    print("✅ Model & files loaded successfully")

except Exception as e:
    print("❌ Model loading failed:", e)

# -------------------------
# HOME ROUTE
# -------------------------
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "RiskRadar Backend Running 🚀",
        "model_loaded": model is not None,
        "features": features
    })

# -------------------------
# PREDICTION ROUTE
# -------------------------
@app.route("/predict", methods=["POST"])
def predict():
    if model is None or scaler is None:
        return jsonify({
            "error": "Model not loaded properly on server"
        }), 500

    try:
        data = request.json or {}

        city = data.get("city")
        area = data.get("area")

        if not city or not area:
            return jsonify({"error": "City and area are required"}), 400

        hour = int(data.get("hour", 18))
        day = int(data.get("day", 3))
        month = int(data.get("month", 6))
        victim_age = int(data.get("victim_age", 25))

        night_factor = 1 if hour >= 20 or hour <= 6 else 0

        input_data = np.array([[hour, day, month, victim_age, night_factor]])
        input_scaled = scaler.transform(input_data)

        risk_prob = model.predict_proba(input_scaled)[0][1]

        risk_level = "HIGH" if risk_prob >= 0.4 else "LOW"

        crowd = crowd_density(hour, "Residential")
        crowd_msg = crowd_alert(crowd)

        return jsonify({
            "city": city,
            "area": area,
            "risk_level": risk_level,
            "risk_probability": round(float(risk_prob), 2),
            "crowd_status": crowd,
            "crowd_alert": crowd_msg,
            "recommendation": (
                "Avoid isolated routes" if risk_level == "HIGH"
                else "Area looks relatively safe"
            )
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -------------------------
# RUN SERVER (LOCAL ONLY)
# -------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
