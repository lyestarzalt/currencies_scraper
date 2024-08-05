import firebase_admin
from firebase_admin import firestore
from datetime import datetime, timedelta
from typing import Dict, List
from models.currency import Currency  

class FirestoreManager:
    def __init__(self):
        self.db = firestore.client()

    def update_currency_trends(self, core_currencies: List[Currency]) -> None:
        """Updates trend data for multiple currencies based on the latest buy rates, using today's date."""
        current_date = datetime.now().date().strftime('%Y-%m-%d')
        cutoff_date = (datetime.now().date() - timedelta(days=730)).strftime('%Y-%m-%d')

        for currency in core_currencies:
            trend_document = self.db.collection('currency-trends').document(currency.currencyCode)
            trend_data: Dict[str, float] = trend_document.get().to_dict() if trend_document.get().exists else {}

            # Record the latest buy rate
            trend_data[current_date] = currency.buy

            # Filter out data older than two years
            filtered_trend_data = {date: rate for date, rate in trend_data.items() if date >= cutoff_date}

            # Persist the updated trend data to Firestore
            trend_document.set(filtered_trend_data)
        
        
    def upload_exchange_rates(self, currencies: List[Currency], collection_name: str) -> None:
        """Uploads exchange rate data to Firestore under a specified collection."""
        exchange_data = {
            currency.currencyCode: {
                "currencyCode": currency.currencyCode,
                "name": currency.name,
                "symbol": currency.symbol,
                "flag": currency.flag,
                "buy": currency.buy,
                "sell": currency.sell,
                "date": currency.date.strftime('%Y-%m-%d'),
                "is_core": currency.is_core
            } for currency in currencies
        }

        current_date = datetime.now().strftime('%Y-%m-%d')
        self.db.collection(collection_name).document(current_date).set(exchange_data)




    def initialize_firestore(self):
        """Initialize Firestore with your project's specific details."""
        cred = firebase_admin.credentials.Certificate('path/to/your/serviceAccountKey.json')
        firebase_admin.initialize_app(cred)


