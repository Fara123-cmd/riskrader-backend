import firebase_admin
import os
import json
from firebase_admin import credentials

def init_firebase():
    if firebase_admin._apps:
        return

    # Case 1️⃣: Render / Production (ENV variable)
    firebase_env = os.environ.get("FIREBASE_SERVICE_ACCOUNT")

    if firebase_env:
        cred = credentials.Certificate(json.loads(firebase_env))
        firebase_admin.initialize_app(cred)
        print("✅ Firebase initialized from ENV variable")

    # Case 2️⃣: Local development (JSON file)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        key_path = os.path.join(base_dir, "serviceAccountKey.json")

        if not os.path.exists(key_path):
            raise FileNotFoundError(
                "❌ serviceAccountKey.json not found AND FIREBASE_SERVICE_ACCOUNT not set"
            )

        cred = credentials.Certificate(key_path)
        firebase_admin.initialize_app(cred)
        print("✅ Firebase initialized from local JSON file")


def send_alert(user_id, message):
    init_firebase()
    print(f"🔥 Firebase Alert Sent to {user_id}: {message}")
