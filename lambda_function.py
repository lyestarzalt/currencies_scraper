"""Lyes Tarzalt"""
from messaging import send_localized_notification
import os
from datetime import datetime,  timedelta
import firebase_admin
from firebase_admin import messaging

from firebase_admin import credentials, firestore
from scraper import DinarScraper
from currency_data_provider import CurrencyDataProvider
from extra_currency_manager import ExtraCurrencyManager
import time


keys = {
    "type": "service_account",
    "project_id": os.getenv("PROJECT_ID"),
    "private_key_id": os.getenv("PRIVATE_KEY_ID"),
    "private_key": os.getenv("PRIVATE_KEY").replace(r'\n', '\n'),
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

# This must be imported after init firebase


def update_trend_data(currency, new_data_date, new_data_buy):
    trend_ref = db.collection('exchange-rate-trends').document(currency)
    trend_data = trend_ref.get().to_dict() if trend_ref.get().exists else {}

    # Add new data
    trend_data[new_data_date.strftime('%Y-%m-%d')] = new_data_buy

    # Ensure only data for the last 2 years is kept
    two_years_ago = (new_data_date - timedelta(days=2 * 365)
                     ).strftime('%Y-%m-%d')
    trend_data = {date: buy for date,
                  buy in trend_data.items() if date >= two_years_ago}

    # Save the updated trend data back to Firestore
    trend_ref.set(trend_data)


def lambda_handler(event, context) -> dict:
    try:
        # Initialize Scraper and Data Provider
        scraper = DinarScraper()
        data_provider = CurrencyDataProvider('countries.json')

        # Fetch core currencies data
        _, core_currencies_list = scraper.get_forex_data()
        core_currencies = {currency.currencyCode: currency for currency in core_currencies_list}

        # Choose a base currency and create ExtraCurrencyManager
        base_currency = core_currencies.get('EUR', None)
        if not base_currency:
            raise ValueError("Base currency not found in core currencies")

        manager = ExtraCurrencyManager(
            base_currency, core_currencies, data_provider)

        # Calculate unofficial exchange rates
        non_core_currencies = manager.calculate_converted_currencies()
        all_currencies = {
            **{currency.currencyCode: currency for currency in non_core_currencies}, **core_currencies}

        # Calculate official exchange rates
        official_currencies = manager.get_official_exchange_rates()

        # Construct the exchange data for Firestore for unofficial rates
        unofficial_exchange_data = {currency_code: {"currencyCode": currency.currencyCode, "name": currency.name,
                                                    "symbol": currency.symbol, "flag": currency.flag, "buy": currency.buy,
                                                    "sell": currency.sell, "date": currency.date, "is_core": currency.is_core}
                                    for currency_code, currency in all_currencies.items()}

        # Construct the exchange data for Firestore for official rates
        official_exchange_data = {currency.currencyCode: {"currencyCode": currency.currencyCode, "name": currency.name,
                                                          "symbol": currency.symbol, "flag": currency.flag, "buy": currency.buy,
                                                          "sell": currency.sell, "date": currency.date, "is_core": currency.is_core}
                                  for currency in official_currencies}

        # Upload the data to Firebase for unofficial rates
        current_date = datetime.now().date()
        db.collection(u'exchange-daily').document(str(current_date)
                                                  ).set(unofficial_exchange_data)

        # Upload the data to Firebase for official rates
        db.collection(
            u'exchange-daily-official').document(str(current_date)).set(official_exchange_data)

        # Update trend data for unofficial rates
        for currency_code in core_currencies.keys():
            if currency_code in unofficial_exchange_data:
                update_trend_data(currency_code, current_date,
                                  unofficial_exchange_data[currency_code]['buy'])

        # Send notifications
        languages = ['en', 'de', 'fr', 'ar', 'es', 'zh']
        for lang in languages:
            send_localized_notification(lang, current_date)

        return {'statusCode': 200, 'body': 'Data updated successfully'}
    except Exception as e:  # Catch all exceptions, not just Firebase errors
        print(f"Error: {e}")
        return {'statusCode': 500, 'body': 'Operation failed'}


if __name__ == "__main__":
    lambda_handler(None, None)
