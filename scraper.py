# Author: Lyes Tarzalt
from dataclasses import dataclass
import re
import datetime
from typing import List, Tuple
import requests


@dataclass
class Currency:
    """

    """
    name: str = None
    buy: float = None
    sell: float = None


def translate_month_to_english(date_str: str) -> str:
    """
    Args:
        date_str (str): Month  in french

    Returns:
        str: Month in English
    """
    french_to_english_months = {
        'Janvier': 'January',
        'Février': 'February',
        'Mars': 'March',
        'Avril': 'April',
        'Mai': 'May',
        'Juin': 'June',
        'Juillet': 'July',
        'Août': 'August',
        'Septembre': 'September',
        'Octobre': 'October',
        'Novembre': 'November',
        'Décembre': 'December'
    }

    for french, english in french_to_english_months.items():
        if french in date_str:
            return date_str.replace(french, english)
    return date_str


class DinarScraper:
    """_summary_

    Raises:
        ValueError: _description_
        ValueError: _description_

    Returns:
        _type_: _description_
    """
    forex_url = "http://www.forexalgerie.com/connect/updateExchange.php"
    devise_dz_url = "https://www.devise-dz.com/square-port-said-alger/"

    def __init__(self) -> None:
        pass

    def get_forex_data(self) -> Tuple[datetime.date, List[Currency]]:
        """_summary_

        Returns:
            Tuple[datetime.date, List[Currency]]: _description_
        """        """Get the latest forex data from the website."""
        raw_data = requests.post(DinarScraper.forex_url,
                                 {'afous': 'moh!12!'}, verify=False, timeout=10).json()
        try:
            latest_data = raw_data[0]
        except IndexError:
            return datetime.date(1970, 1, 1), Currency()
        # map the data to a list of Currency objects
        currencies = []
        create_date_time = datetime.datetime.strptime(
            latest_data["create_date_time"], "%d-%m-%Y %H:%M:%S").date()
        for key, value in latest_data.items():
            if key.endswith("_sell"):
                name = key[:-5]
                sell = float(value)
                buy = float(latest_data[name + "_buy"])
                currencies.append(Currency(name=name, buy=buy, sell=sell))
        return create_date_time, currencies

    def replace_symbol(self, symbol: str) -> str:
        """_summary_

        Args:
            symbol (str): _description_

        Returns:
            str: _description_
        """
        symbol_map = {'€': 'eur', '$': 'usd', '£': 'gbp', 'EAD': 'aed'}
        return symbol_map.get(symbol, symbol)

    def extract_currency_data(self, html_content):
        """_summary_

        Args:
            html_content (_type_): _description_

        Returns:
            _type_: _description_
        """
        currencies = []
        table_matches = re.findall(
            r'<table.*?>(.*?)</table>', html_content, re.DOTALL)

        for table in table_matches:
            row_matches = re.findall(r'<tr.*?>(.*?)</tr>', table, re.DOTALL)
            for row in row_matches:
                cell_matches = re.findall(
                    r'<td.*?>(?:<a.*?>)?(.*?)(?:</a>)?</td>', row, re.DOTALL)
                if len(cell_matches) >= 3:
                    currency_name_match = re.search(
                        r'\((.*?)\)', cell_matches[0])
                    if currency_name_match:
                        currency_name = self.replace_symbol(
                            currency_name_match.group(1).lower())
                        buy_value = float(cell_matches[1].strip(
                            ' DA').replace(',', '.'))
                        sell_value = float(
                            cell_matches[2].strip(' DA').replace(',', '.'))
                        currencies.append(
                            Currency(name=currency_name, buy=buy_value, sell=sell_value))

        return currencies

    def get_devise_dz_data(self) -> Tuple[datetime.date, List[Currency]]:
        """Scrape devise website

        Raises:
            ValueError: No currencies shown

        Returns:
            Tuple[datetime.date, List[Currency]]: _description_
        """
        try:
            response = requests.get(self.devise_dz_url, timeout=10)
            response.raise_for_status()
        except requests.exceptions.HTTPError as error:
            print(f"HTTP error occurred: {error}")
            return datetime.date(1970, 1, 1), []

        try:
            html_content = response.text
            update_date_match = re.search('Mise à jour : (.*?)<', html_content)
            if update_date_match:
                update_date_str = translate_month_to_english(
                    update_date_match.group(1))
                update_date = datetime.datetime.strptime(
                    update_date_str, '%d %B %Y').date()

            else:
                raise ValueError('Update date not found')

            currencies = self.extract_currency_data(html_content)
            return update_date, currencies

        except Exception as e:
            print(f"Error parsing the webpage: {e}")
            return datetime.date(1970, 1, 1), []


if __name__ == "__main__":
    pass
