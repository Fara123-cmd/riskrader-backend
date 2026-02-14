import os
import json
import firebase_admin
from firebase_admin import credentials

# Initialize Firebase only once
if not firebase_admin._apps:
    firebase_json = json.loads(os.environ.get("FIREBASE_SERVICE_ACCOUNT"))
    cred = credentials.Certificate(firebase_json)
    firebase_admin.initialize_app(cred)

def send_alert(user_id, message):
    # Later you can replace this with real Firebase push / Firestore logic
    print(f"🔥 Firebase Alert Sent to {user_id}: {message}")
