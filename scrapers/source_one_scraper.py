from datetime import datetime
from typing import List
import requests
from scrapers.base import CurrencyScraperBase
from models.currency import Currency
from utils.config import SOURCE_ONE_URL
from utils.logger import get_logger 
from exceptions.data_exceptions import DataFetchError, DataParseError\

logger = get_logger('SourceOneScraper')


class SourceOneScraper(CurrencyScraperBase):


    def fetch_data(self) -> dict:
        try:
            response = requests.post(
                SOURCE_ONE_URL, {"afous": "moh!12!"}, verify=False, timeout=10
            )
            response.raise_for_status()
            logger.info("Data successfully retrieved from source.")
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Fetching error: {str(e)}", exc_info=True)
            raise DataFetchError(f"Data retrieval failed: {str(e)}") from e



    def parse_data(self, raw_data: dict) -> List[Currency]:
        if not raw_data:
            logger.warning("Empty dataset received; nothing to parse.")
            raise DataParseError("Empty dataset; no data to parse.")
        
        try:
            latest_data = raw_data[0]
            create_date_time = datetime.strptime(
                latest_data["create_date_time"], "%d-%m-%Y %H:%M:%S").date()
            
            currencies = []
            for key, value in latest_data.items():
                if key.endswith("_sell"):
                    currency_code = key[:-5].upper()
                    sell = float(value)
                    buy = float(latest_data.get(f"{currency_code.lower()}_buy", 0))
                    currency = Currency(
                        currencyCode=currency_code,
                        buy=buy,
                        sell=sell,
                        update_date=create_date_time,
                        is_core=True,
                    )
                    currencies.append(currency)
                    logger.debug(f"{currency_code}: Buy={buy}, Sell={sell}")
            return currencies
        except KeyError as e:
            logger.error(f"Data parsing error: Missing key {str(e)}", exc_info=True)
            raise DataParseError("Parsing failed due to missing data.")
        
        
