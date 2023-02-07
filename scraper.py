# Author: Lyes Tarzalt
from dataclasses import dataclass
import datetime
import requests
import pandas as pd
import re


@dataclass
class Currency:
    name: str = None
    buy: float = None
    sell: float = None


class DinarScraper:
    forex_url = "http://www.forexalgerie.com/connect/updateExchange.php"
    devise_dz_url = "https://www.devise-dz.com/square-port-said-alger/"

    def __init__(self) -> None:
        now_date = datetime.date.today()

    def get_forex_data(self) -> tuple[datetime.date, list[Currency]]:
        """Get the latest forex data from the website."""
        raw_data = requests.post(DinarScraper.forex_url,
                                 {'afous': 'moh!12!'}, verify=False).json()
        try:
            latest_data = raw_data[0]
        except IndexError:
            return datetime.date(1970, 1, 1), Currency()
        # map the data to a list of Currency objects
        currencies = []
        create_date_time = datetime.datetime.strptime(
            latest_data["create_date_time"], "%d-%m-%Y %H:%M:%S")
        for key, value in latest_data.items():
            if key.endswith("_sell"):
                name = key[:-5]
                sell = float(value)
                buy = float(latest_data[name + "_buy"])
                currencies.append(Currency(name=name, buy=buy, sell=sell))
        return create_date_time, currencies

    def replace_symbol(self, symbol: str):
        symbol_map = {'€': 'eur', '$': 'usd', '£': 'gbp', 'EAD': 'aed'}
        return symbol_map.get(symbol, symbol)

    def get_devise_dz_data(self) -> list[Currency]:
        try:
            response = requests.get(
                'https://www.devise-dz.com/square-port-said-alger/')
            response.raise_for_status()
        except requests.exceptions.HTTPError as error:
            print(f"An error occured while making the request: {error}")
            return datetime.date(1970, 1, 1), Currency()

        try:
            df_list = pd.read_html(response.content)

        except ValueError as error:
            print(
                f"An error occured while parsing the response content: {error}")
            return datetime.date(1970, 1, 1), Currency()
        try:
            html_content = response.text
            update_date = re.search(
                'Mise à jour : (.*?)<', html_content).group(1)
            update_date = datetime.strptime(update_date, '%d %B %Y')
        except (AttributeError, ValueError) as err:
            return datetime.date(1970, 1, 1), Currency()
        euro_usd = df_list[0]
        rest_currencies = df_list[1]
        rest_currencies.rename(
            columns={0: 'Devises', 1: 'Achat', 2: 'Vente'}, inplace=True)
        euro_usd.set_index('Devises')
        rest_currencies.set_index('Devises')
        merged_currencies = pd.concat([rest_currencies, euro_usd])

        merged_currencies['Achat'] = merged_currencies['Achat'].str.replace(
            ',', '.')
        merged_currencies['Achat'] = merged_currencies['Achat'].str.strip(
            ' DA')
        merged_currencies['Vente'] = merged_currencies['Vente'].str.replace(
            ',', '.')
        merged_currencies['Vente'] = merged_currencies['Vente'].str.strip(
            ' DA')

        currencies_names = merged_currencies['Devises'].to_list()

        currencies = []
        for name in currencies_names:
            symbol = name[name.find('(')+1:name.find(')')]
            symbol = symbol.lower()
            symbol = symbol.replace('€', 'eur')
            symbol = symbol.replace('$', 'usd')
            symbol = symbol.replace('£', 'gbp')
            symbol = symbol.replace('ead', 'aed')
            currencies.append(symbol)

        merged_currencies['Vente'] = pd.to_numeric(
            merged_currencies['Vente'])
        merged_currencies['Achat'] = pd.to_numeric(
            merged_currencies['Achat'])

        merged_currencies['Devises'] = currencies
        merged_currencies.set_index('Devises', inplace=True)
        merged_currencies.rename(
            columns={'Achat': 'buy', 'Vente': 'sell'}, inplace=True)

        currencies = []
        for name, values in merged_currencies.iterrows():
            currencies.append(
                Currency(name=name, buy=values['buy'], sell=values['sell']))

        return update_date, currencies


if __name__ == "__main__":
    pass
