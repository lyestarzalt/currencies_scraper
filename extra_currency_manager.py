import requests
from model import Currency
from datetime import datetime
from currency_data_provider import CurrencyDataProvider


class ExtraCurrencyManager:
    def __init__(self, base_currency, core_currencies, currency_provider):
        self.base_currency = base_currency
        self.core_currencies = core_currencies
        self.currency_provider = currency_provider

    def fetch_exchange_rates(self):
        url = f"https://open.er-api.com/v6/latest/{self.base_currency.currencyCode}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data['rates']
        else:
            raise Exception('Failed to fetch exchange rates')

    def calculate_converted_currencies(self):
        rates = self.fetch_exchange_rates()
        converted_currencies = []

        base_currency_buy_rate = self.core_currencies.get(
            self.base_currency.currencyCode, Currency()).buy
        base_currency_sell_rate = self.core_currencies.get(
            self.base_currency.currencyCode, Currency()).sell

        for currency_code, rate_to_usd in rates.items():
            if currency_code != self.base_currency.currencyCode:
                # Convert from USD to the target currency
                converted_buy_rate = base_currency_buy_rate / rate_to_usd
                converted_sell_rate = base_currency_sell_rate / rate_to_usd
                # Get additional details from CurrencyDataProvider
                additional_details = self.currency_provider.get_currency_details(
                    currency_code)

                currency = Currency(
                    currencyCode=currency_code,
                    name=additional_details.get('name', ''),
                    symbol=additional_details.get('symbol', ''),
                    flag=additional_details.get('flag', ''),
                    buy=converted_buy_rate,
                    sell=converted_sell_rate,
                    date=datetime.now().strftime("%Y-%m-%d"),
                    is_core=False
                )
                converted_currencies.append(currency)

        return converted_currencies

    def get_official_exchange_rates(self):
        self.base_currency.currencyCode = 'DZD'
        rates = self.fetch_exchange_rates()
        official_currencies = []

        # TODO Margins: Adjust these values
        buy_margin = 1.02  # 2% higher for buying rates
        sell_margin = 0.98  # 2% lower for selling rates
        _core_currencies = {'CNY', 'USD', 'CHF', 'TRY', 'AED',
                            'EUR', 'CAD', 'SAR', 'GBP'}  # Define core currencies

        for currency_code, rate in rates.items():
            if currency_code != self.base_currency.currencyCode:
                is_core = currency_code in _core_currencies
                buy_rate = (1 / rate) * buy_margin
                sell_rate = (1 / rate) * sell_margin
                additional_details = self.currency_provider.get_currency_details(
                    currency_code)
                currency = Currency(
                    currencyCode=currency_code,
                    name=additional_details.get('name', ''),
                    symbol=additional_details.get('symbol', ''),
                    flag=additional_details.get('flag', ''),
                    buy=buy_rate,
                    sell=sell_rate,
                    date=datetime.now().strftime("%Y-%m-%d"),
                    is_core=is_core
                )
                official_currencies.append(currency)

        return official_currencies


if __name__ == "__main__":
    base_currency = Currency(currencyCode='DZD')
    core_currencies = {}
    data_provider = CurrencyDataProvider('countries.json')
    manager = ExtraCurrencyManager(
        base_currency, core_currencies, data_provider)
    official_rates: list[Currency] = manager.get_official_exchange_rates()
    for cur in official_rates:
        if cur.currencyCode.lower() == 'eur':
            print(cur)
