import re
from datetime import datetime
from typing import List
import requests
from bs4 import BeautifulSoup
from scrapers.base import CurrencyScraperBase
from models.currency import Currency
from utils.logger import get_logger
from exceptions.data_exceptions import DataFetchError, DataParseError
from utils.config import SOURCE_TWO_URL

logger = get_logger('SourceTwoScraper')

class SourceTwoScraper(CurrencyScraperBase):
    def fetch_data(self) -> str:
        try:
            response = requests.get(SOURCE_TWO_URL, timeout=10)
            response.raise_for_status()
            logger.info(f"Successfully fetched data from {SOURCE_TWO_URL}.")
            return response.text
        except requests.RequestException as e:
            error_msg = f"Error fetching data: {str(e)}"
            logger.error(error_msg)
            raise DataFetchError(error_msg) from e

    def parse_data(self, html_content: str) ->  List[Currency]:
        try:
            update_date_match = re.search('Mise à jour : (.*?)<', html_content)
            if update_date_match:
                update_date_str = self.translate_month_to_english(update_date_match.group(1))
                update_date = datetime.strptime(update_date_str, '%d %B %Y').date()
            else:
                raise ValueError('Update date not found')

            currencies = self.extract_currency_data(html_content, update_date)
            return currencies
        except Exception as e:
            error_msg = f"Error parsing JSON data: {e}"
            logger.error(error_msg)
            raise DataParseError(error_msg)

    def replace_symbol(self, symbol: str) -> str:
        """_summary_

        Args:
            symbol (str): _description_

        Returns:
            str: _description_
        """
        symbol_map = {'€': 'eur', '$': 'usd', '£': 'gbp', 'EAD': 'aed'}
        return symbol_map.get(symbol, symbol)
    def translate_month_to_english(self, date_str: str) -> str:
        french_to_english_months = {
            'Janvier': 'January', 'Février': 'February', 'Mars': 'March',
            'Avril': 'April', 'Mai': 'May', 'Juin': 'June',
            'Juillet': 'July', 'Aout': 'August', 'Septembre': 'September',
            'Octobre': 'October', 'Novembre': 'November', 'Décembre': 'December'
        }
        for french, english in french_to_english_months.items():
            date_str = date_str.replace(french, english)
        return date_str

    def extract_currency_data(self, html_content: str, update_date) -> List[Currency]:
        currencies = []
        soup = BeautifulSoup(html_content, 'html.parser')

        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 3:
                    currency_name = cells[0].get_text(strip=True)
                    buy_value = cells[1].get_text(strip=True)
                    sell_value = cells[2].get_text(strip=True)

                    currency_name_match = re.search(r'\((.*?)\)', currency_name)
                    if currency_name_match:
                        currency_code = self.replace_symbol(currency_name_match.group(1).upper())
                        buy_value = float(buy_value.strip(' DA').replace(',', '.'))
                        sell_value = float(sell_value.strip(' DA').replace(',', '.'))

                        currency = Currency(
                            currencyCode=currency_code.upper(),
                            buy=buy_value,
                            sell=sell_value,
                            update_date=update_date,
                            is_core=True
                        )
                        currencies.append(currency)

        return currencies



