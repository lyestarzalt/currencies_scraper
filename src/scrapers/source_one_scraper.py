from datetime import datetime
from typing import List, Tuple
import requests
from scrapers.base import CurrencyScraperBase
from models.currency import Currency
from utils.logger import get_logger  # Ensure this import is correctly pointing to your logger setup

logger = get_logger('SourceOneScraper')

class SourceOneScraper(CurrencyScraperBase):
    forex_url = "http://www.forexalgerie.com/connect/updateExchange.php"

    def fetch_data(self) -> dict:
        try:
            response = requests.post(
                self.forex_url, {"afous": "moh!12!"}, verify=False, timeout=10
            )
            response.raise_for_status()
            logger.info("Successfully fetched data from Forex Algerie.")
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error fetching data from {self.forex_url}: {str(e)}")
            return {}

    def parse_data(self, raw_data: dict) -> Tuple[datetime, List[Currency]]:
        try:
            latest_data = raw_data[0]
        except IndexError:
            logger.warning("No data found to parse.")
            return datetime.now().date(), []

        currencies = []
        create_date_time = datetime.strptime(
            latest_data["create_date_time"], "%d-%m-%Y %H:%M:%S"
        ).date()

        for key, value in latest_data.items():
            if key.endswith("_sell"):
                currency_code = key[:-5].upper()
                sell = float(value)
                buy = float(latest_data.get(f"{currency_code.lower()}_buy", 0))

                currency = Currency(
                    currencyCode=currency_code,
                    buy=buy,
                    sell=sell,
                    date=create_date_time.strftime("%Y-%m-%d"),
                    is_core=True,
                )
                currencies.append(currency)
                logger.debug(f"Processed currency {currency_code} with buy {buy} and sell {sell}.")

        return create_date_time, currencies

    def get_data(self) -> Tuple[datetime, List[Currency]]:
        raw_data = self.fetch_data()
        if raw_data:
            logger.info("Parsing data.")
            return self.parse_data(raw_data)
        else:
            logger.info("No data received to process.")
            return datetime.now().date(), []