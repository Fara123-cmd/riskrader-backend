from flask import Flask, request, jsonify
from flask_cors import CORS
import xgboost as xgb
import pickle
import numpy as np

from crowd_density import crowd_density, crowd_alert
from firebase_service import send_alert

# -------------------------
# APP SETUP
# -------------------------
app = Flask(__name__)
CORS(app)

# -------------------------
# LOAD MODEL FILES
# -------------------------
model = xgb.XGBClassifier()
model.load_model("crime_model.json")

with open("scaler.pkl", "rb") as f:
    scaler = pickle.load(f)

with open("features.pkl", "rb") as f:
    features = pickle.load(f)

# -------------------------
# HOME ROUTE
# -------------------------
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "RiskRadar Backend Running 🚀",
        "model": "XGBoost Risk Prediction",
        "features": features
    })

# -------------------------
# PREDICTION ROUTE
# -------------------------
@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.json or {}

        # REQUIRED
        city = data.get("city")
        area = data.get("area")

        if not city or not area:
            return jsonify({"error": "City and area are required"}), 400

        # OPTIONAL INPUTS
        hour = int(data.get("hour", 18))
        day = int(data.get("day", 3))
        month = int(data.get("month", 6))
        victim_age = int(data.get("victim_age", 25))

        night_factor = 1 if hour >= 20 or hour <= 6 else 0

        # MODEL INPUT (SAME ORDER AS TRAINING)
        input_data = np.array([[hour, day, month, victim_age, night_factor]])
        input_scaled = scaler.transform(input_data)

        # PREDICTION
        risk_prob = model.predict_proba(input_scaled)[0][1]

        if risk_prob >= 0.4:
            risk_level = "HIGH"
        else:
            risk_level = "LOW"

        # CROWD LOGIC
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
# RUN SERVER
# -------------------------
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

