from scrapers.scraper_controller import ScraperController
from currency_management.currency_manager import CurrencyManager
from database.firestore_manager import FirestoreManager
from utils.logger import get_logger
from typing import Any, Dict

logger = get_logger("App")


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    logger.info("Starting the application.")
    firestore_manager = FirestoreManager()
    scraper_controller = ScraperController()

    try:
        currencies = scraper_controller.fetch_currencies()
        if currencies:
            logger.info("Successfully retrieved currency data.")
        else:
            logger.error("No currencies fetched, exiting application.")
            return {
                "statusCode": 500,
                "body": "No currencies fetched, exiting application.",
            }

        currency_manager = CurrencyManager(core_currencies=currencies)
        unofficial_rates = currency_manager.generate_unofficial_rates()
        official_rates = currency_manager.generate_official_rates()

        firestore_manager.update_currency_trends(
            currencies, collection_name="currency-trends_test"
        )
        firestore_manager.upload_exchange_rates(
            currencies=unofficial_rates, collection_name="exchange-daily_test"
        )
        firestore_manager.upload_exchange_rates(
            currencies=official_rates, collection_name="exchange-daily-official_test"
        )
        logger.info(f"Generated unofficial and official rates. ")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return {"statusCode": 500, "body": f"An error occurred: {e}"}

    return {"statusCode": 200, "body": "Execution completed successfully."}


if __name__ == "__main__":
    lambda_handler({}, {})
