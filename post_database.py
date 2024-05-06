"""Lyes Tarzalt"""
import os
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
from scraper import DinarScraper


keys = {
    "type": "service_account",
    "project_id": os.getenv("PROJECT_ID"),
    "private_key_id": os.getenv("PRIVATE_KEY_ID"),
    "private_key": os.getenv("PRIVATE_KEY"),
    "client_email": os.getenv("CLIENT_EMAIL"),
    "client_id": os.getenv("CLIENT_ID"),
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": os.getenv("CLIENT_X509_CERT_URL")
}

cred = credentials.Certificate(keys)
firebase_admin.initialize_app(cred)
db = firestore.client()

def lambda_handler(event, context) -> dict:
    try:
        sr = DinarScraper()

        first_source = sr.get_forex_data()
        second_source = sr.get_devise_dz_data()

        # Determine the latest data source
        latest_source = first_source if first_source[0] > second_source[0] else second_source

        # Construct the exchange data
        exchange_data = {currency.name: {"buy": currency.buy, "sell": currency.sell}
                         for currency in latest_source[1]}

        # Upload the data to Firebase
        db.collection(
            u'exchange-daily').document(str(datetime.now().date())).set(exchange_data)

        return {
            'statusCode': 200,
            'body': 'Data updated successfully'
        }
    except firebase_admin.exceptions.FirebaseError as fe:
        print(f"Firebase error: {fe}")
        return {
            'statusCode': 500,
            'body': 'Firebase operation failed'
        }
    except Exception as e:
        print(f"General error: {e}")
        return {
            'statusCode': 500,
            'body': 'An error occurred'
        }


if __name__ == "__main__":
    # Running locally
    os.environ["PROJECT_ID"] = None
    os.environ["PRIVATE_KEY_ID"] = None
    os.environ["PRIVATE_KEY"] = None
    os.environ["CLIENT_EMAIL"] = None
    os.environ["CLIENT_ID"] = None
    os.environ["CLIENT_X509_CERT_URL"] = None

    lambda_handler(None, None)
