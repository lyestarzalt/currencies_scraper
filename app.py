from scrapers.scraper_controller import ScraperController
from currency_management.currency_manager import CurrencyManager
from database.firestore_manager import FirestoreManager
from models.currency import Currency
from utils.logger import get_logger
from datetime import date

logger = get_logger('App')

def main() -> None:

    logger.info("Starting the application.")
    firestore_manager = FirestoreManager()
    scraper_controller = ScraperController()

    try:
        currencies = scraper_controller.fetch_currencies()
        if currencies:
            logger.info("Successfully retrieved currency data.")
        else:
            logger.error("No currencies fetched, exiting application.")
            return
        currency_manager = CurrencyManager(base_currency='usd', core_currencies=currencies)
        unofficial_rates = currency_manager.generate_unofficial_rates()
        official_rates = currency_manager.generate_official_rates()
        
        firestore_manager.update_currency_trends(currencies, collection_name='currency-trends_test')
        firestore_manager.upload_exchange_rates(currencies=unofficial_rates, collection_name='exchange-daily_test') 
        firestore_manager.upload_exchange_rates(currencies=official_rates, collection_name='exchange-daily-official_test')  
        logger.info(f"Generated unofficial and official rates. ")

    except Exception as e:
        logger.error(f"An error occurred: {e}")

if __name__ == '__main__':
    main()














