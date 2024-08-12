import boto3
import json
import logging
from datetime import datetime
from typing import List
from models.currency import Currency
from exceptions.data_exceptions import DataFetchError, DataParseError
from utils.config import SCRAPER_LAMBDAS
from utils.logger import get_logger

logger = get_logger("ScraperController")


class ScraperController:
    def __init__(self) -> None:
        self.lambda_client = boto3.client("lambda")
        self.scrapers = SCRAPER_LAMBDAS

    def invoke_lambda(self, function_name: str) -> str:
        try:
            response = self.lambda_client.invoke(
                FunctionName=function_name, InvocationType="RequestResponse"
            )
            if response["StatusCode"] == 200:
                response_payload = json.loads(
                    response["Payload"].read().decode("utf-8")
                )
                if response_payload["statusCode"] == 200:
                    return response_payload["body"]
                else:
                    raise DataFetchError(response_payload["body"])
            else:
                raise DataFetchError(
                    f"Lambda {function_name} failed with status code {response['StatusCode']}"
                )
        except Exception as e:
            raise DataFetchError(
                f"Error invoking Lambda {function_name}: {str(e)}"
            ) from e

    def parse_data(self, json_content: str) -> List[Currency]:
        try:
            data = json.loads(json_content)
            currencies = []
            update_date = datetime.strptime(data["update_time"], "%d-%m-%Y").date()

            for item in data["currencies"]:
                currency = Currency(
                    currencyCode=item["currencyCode"],
                    buy=float(item["buy"]),
                    sell=float(item["sell"]),
                    update_date=update_date,
                    is_core=True,
                )
                currencies.append(currency)
            return currencies
        except Exception as e:
            raise DataParseError(f"Error parsing JSON data: {e}")

    def fetch_currencies(self) -> List[Currency]:
        for function_name in self.scrapers:
            try:
                logger.info(f"Attempting to fetch data with {function_name}")
                json_content = self.invoke_lambda(function_name)
                currency_data = self.parse_data(json_content)
                if currency_data:
                    logger.info(f"Successfully fetched data with {function_name}")
                    return currency_data
            except (DataFetchError, DataParseError) as e:
                logger.error(f"Failed to fetch data with {function_name}: {e}")
        raise Exception("All scrapers failed to fetch data.")
