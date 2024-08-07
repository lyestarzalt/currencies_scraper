import json
import boto3
from typing import List
from datetime import datetime
from scrapers.base import CurrencyScraperBase
from models.currency import Currency
from utils.logger import get_logger
from exceptions.data_exceptions import DataFetchError, DataParseError
from utils.config import SOURCE_THREE_URL

logger = get_logger('SourceThreeScraper')

class SourceThreeScraper(CurrencyScraperBase):
    lambda_function_name = SOURCE_THREE_URL

    def fetch_data(self) -> str:
        client = boto3.client('lambda')
        try:
            response = client.invoke(
                FunctionName=self.lambda_function_name,
                InvocationType='RequestResponse',
            )
            response_payload = json.loads(response['Payload'].read().decode('utf-8'))
            logger.info(f"Successfully fetched data from {self.lambda_function_name}.")
            return response_payload['body']
        except Exception as e:
            error_msg = f"Error fetching data: {str(e)}"
            logger.error(error_msg)
            raise DataFetchError(error_msg) from e

    def parse_data(self, json_content: str) -> List[Currency]:
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
