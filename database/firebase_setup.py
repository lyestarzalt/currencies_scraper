import os
import firebase_admin
from firebase_admin import credentials, firestore
import json


def initialize_firebase(firebase_credentials: dict) -> None:
    """
    Initializes the Firebase Admin SDK if it hasn't been initialized already.
    Removes the FIRESTORE_EMULATOR_HOST environment variable if it exists.
    """
    os.environ.pop("FIRESTORE_EMULATOR_HOST", None)
    if not firebase_admin._apps:
        cred = credentials.Certificate(firebase_credentials)
        firebase_admin.initialize_app(cred)


def get_firestore_client(firebase_credentials: dict) -> firestore.Client:
    """
    Returns a Firestore client configured for the current environment.

    Returns:
        firestore.Client: The Firestore client.
    """
    initialize_firebase(firebase_credentials)
    return firestore.client()
