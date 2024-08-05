
import sys
sys.path.append('src')  

from scraper_management.scraper_controller import run_first_scraper
from currency_management.currency_manager import CurrencyManager
from database.firestore_manager import FirestoreManager
from models.currency import Currency
from utils.logger import get_logger
logger = get_logger('App')
def main():
    scrape_time, currencies = run_first_scraper()

    # Initialize and use the CurrencyManager
    currency_manager = CurrencyManager(base_currency=Currency(currencyCode='USD',buy=0,sell=0), core_currencies=currencies)
    
    unof = currency_manager.generate_unofficial_rates()
    off = currency_manager.generate_official_rates()


if __name__ == '__main__':
    main()
