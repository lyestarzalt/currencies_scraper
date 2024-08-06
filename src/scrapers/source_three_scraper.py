import os
from typing import List
from datetime import datetime
import json
import requests
from scrapers.base import CurrencyScraperBase
from models.currency import Currency
from utils.logger import get_logger
from exceptions.data_exceptions import DataFetchError, DataParseError

from dotenv import load_dotenv

load_dotenv()

logger = get_logger('SourceThreeScraper')
LAMBDA_URL = os.getenv('SOURCE_THREE_URL', 'default_lambda_url')

class SourceThreeScraper(CurrencyScraperBase):
    lambda_url = LAMBDA_URL

    def fetch_data(self) -> str:
        try:
            response = requests.get(self.lambda_url, timeout=10)
            response.raise_for_status()
            logger.info(f"Successfully fetched data from {self.lambda_url}.")
            return response.text
        except requests.RequestException as e:
            error_msg = f"Error fetching data: {str(e)}"
            logger.error(error_msg)
            raise DataFetchError(error_msg) from e


    def parse_data(self, json_content: str) ->List[Currency]:
        try:
            data = json.loads(json_content)
            currencies = []
            update_date = datetime.strptime(data['update_time'], '%d-%m-%Y').date()

            for item in data['currencies']:
                currency = Currency(
                    currencyCode=item['currencyCode'],
                    buy=float(item['buy']),
                    sell=float(item['sell']),
                    update_date=update_date,
                    is_core=True 
                )
                currencies.append(currency)
            return currencies
        except Exception as e:
            error_msg = f"Error parsing JSON data: {e}"
            logger.error(error_msg)
            raise DataParseError(error_msg)


