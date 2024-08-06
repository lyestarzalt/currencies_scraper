import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

def initialize_firebase():
    os.environ.pop('FIRESTORE_EMULATOR_HOST', None)
    if not firebase_admin._apps:
        env = os.getenv('ENV', 'staging')  

        if env == 'production':
            firebase_creds_json = os.getenv('FIREBASE_CREDENTIALS_PRODUCTION')
        else:
            firebase_creds_json = os.getenv('FIREBASE_CREDENTIALS_STAGING')

        if firebase_creds_json is None:
            raise ValueError(f"No Firebase credentials set for {env} environment.")

        firebase_creds = json.loads(firebase_creds_json)
        
        cred = credentials.Certificate(firebase_creds)
        firebase_admin.initialize_app(cred)

def get_firestore_client():
    """Returns a Firestore client configured for the current environment."""
    initialize_firebase()
    return firestore.client()
