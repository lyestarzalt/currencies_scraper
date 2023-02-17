import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from datetime import datetime
from scraper import DinarScraper
from dotenv import load_dotenv
import os

def lambda_handler(event, context) -> dict:

    try:
        sr = DinarScraper()

        first_source = sr.get_forex_data()
        second_source = sr.get_devise_dz_data()

        # see who has the latest data
        if first_source[0] > second_source[0]:
            sell_dict = {
                currency.name: currency.sell for currency in first_source[1]}
            buy_dict = {
                currency.name: currency.buy for currency in first_source[1]}
        else:
            sell_dict = {
                currency.name: currency.sell for currency in second_source}
            buy_dict = {
                currency.name: currency.buy for currency in second_source}

        # upload the data to firebase
        
       
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
        db.collection(u'exchange-daily').document(str(datetime.now().date())
                                                  ).set({"anis": [sell_dict, buy_dict]})

        return {
            'statusCode': 200,
            'body': 'Data updated successfully'
        }
    except Exception as e:
        print(e)
        return {
            'statusCode': 400,
            'body': f'An error occured'
        }


if __name__ == "__main__":
    # Running locally
    load_dotenv()
    lambda_handler(None, None)
