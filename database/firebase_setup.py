import os
import firebase_admin
from firebase_admin import credentials, firestore
from utils.config import FIREBASE_CREDENTIALS

def initialize_firebase() -> None:
    os.environ.pop('FIRESTORE_EMULATOR_HOST', None)
    if not firebase_admin._apps:
        cred = credentials.Certificate(FIREBASE_CREDENTIALS)
        firebase_admin.initialize_app(cred)

def get_firestore_client():
    """Returns a Firestore client configured for the current environment."""
    initialize_firebase()
    return firestore.client()