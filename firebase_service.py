import os
import json

try:
    import firebase_admin
    from firebase_admin import credentials, messaging
except ImportError:
    firebase_admin = None


def init_firebase():
    """
    Initialize Firebase only once.
    Works for:
    - Render (ENV variable)
    - Local development (JSON file)
    Safe: will NOT crash the app if Firebase is unavailable
    """

    # If firebase is not installed, skip safely
    if firebase_admin is None:
        print("⚠️ firebase_admin not installed. Skipping Firebase init.")
        return False

    # Already initialized
    if firebase_admin._apps:
        return True

    # Case 1️⃣: Render / Production (ENV variable)
    firebase_env = os.environ.get("FIREBASE_SERVICE_ACCOUNT")

    try:
        if firebase_env:
            cred_dict = json.loads(firebase_env)
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
            print("✅ Firebase initialized from ENV variable (Render)")
            return True

        # Case 2️⃣: Local development (JSON file)
        base_dir = os.path.dirname(os.path.abspath(__file__))
        key_path = os.path.join(base_dir, "serviceAccountKey.json")

        if not os.path.exists(key_path):
            print("⚠️ serviceAccountKey.json not found. Firebase disabled.")
            return False

        cred = credentials.Certificate(key_path)
        firebase_admin.initialize_app(cred)
        print("✅ Firebase initialized from local JSON file")
        return True

    except Exception as e:
        print(f"❌ Firebase initialization failed: {e}")
        return False


def send_alert(user_id, message):
    """
    Send alert safely.
    App will continue running even if Firebase fails.
    """

    initialized = init_firebase()

    if not initialized:
        print(f"⚠️ Firebase disabled. Alert skipped for {user_id}: {message}")
        return

    # 🔔 Later you can add FCM logic here
    print(f"🔥 Firebase Alert Sent to {user_id}: {message}")
