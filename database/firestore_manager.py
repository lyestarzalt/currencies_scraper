from datetime import datetime, timedelta
from typing import Dict, List
from models.currency import Currency  
from database.firebase_setup import get_firestore_client 
from utils.logger import get_logger
from utils.config import FIREBASE_CREDENTIALS
import sys

logger = get_logger('FirestoreManager')

class FirestoreManager:
    def __init__(self) -> None:
        self.db = get_firestore_client(FIREBASE_CREDENTIALS)

    def update_currency_trends(self, core_currencies: List[Currency], collection_name: str) -> None:
        """Updates trend data for multiple currencies based on the latest buy rates, using today's date."""
        try:
            current_date = datetime.now().date().strftime('%Y-%m-%d')
            cutoff_date = (datetime.now().date() - timedelta(days=730)).strftime('%Y-%m-%d')
            for currency in core_currencies:
                trend_document = self.db.collection(collection_name).document(currency.currencyCode)
                trend_data: Dict[str, float] = trend_document.get().to_dict() if trend_document.get().exists else {}
                trend_data[current_date] = currency.buy
                filtered_trend_data = {date: rate for date, rate in trend_data.items() if date >= cutoff_date}
                trend_document.set(filtered_trend_data)
            logger.info("Currency trends updated successfully.")
        except Exception as e:
            logger.error(f"Failed to update currency trends: {e}", exc_info=True)
            raise

    def upload_exchange_rates(self, currencies: List[Currency], collection_name: str) -> None:
        """Uploads exchange rate data to Firestore under a specified collection."""
        try:
            exchange_data = {
                currency.currencyCode: {
                    "currencyCode": currency.currencyCode,
                    "name": currency.name,
                    "symbol": currency.symbol,
                    "flag": currency.flag,
                    "buy": currency.buy,
                    "sell": currency.sell,
                    "date": datetime.combine(currency.update_date, datetime.min.time()),  
                    "is_core": currency.is_core
                } for currency in currencies
            }
            current_date = datetime.now().strftime('%Y-%m-%d')
            logger.info(f"Attempting to write data to Firestore. {collection_name}, {len(currencies)} entries. data size: {sys.getsizeof(exchange_data)} bytes.")
            self.db.collection(collection_name).document(current_date).set(exchange_data)
            logger.info(f"Exchange rates uploaded successfully. {collection_name}")
        except Exception as e:
            logger.error(f"Failed to upload exchange rates: {e}", exc_info=True)
            raise
