import requests
from datetime import datetime
from typing import Dict, List
from models.currency import Currency
from utils.logger import get_logger
from utils.currency_exclusions import is_currency_excluded
logger = get_logger('CurrencyManager')


class CurrencyManager:
    def __init__(self, base_currency: Currency, core_currencies: List[Currency]):
        self.base_currency: Currency = base_currency
        self.core_currencies: List[Currency] = core_currencies

    def fetch_exchange_rates(self) -> Dict[str, float]:
        """Fetch exchange rates for the base currency from an external API."""
        url = f"https://open.er-api.com/v6/latest/{self.base_currency.currencyCode}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            logger.info(f"Successfully fetched exchange rates for {self.base_currency.currencyCode}")
            return data['rates']
        except requests.RequestException as e:
            logger.error(f"Error fetching data from {url}: {e}")
            return {}

    def generate_unofficial_rates(self) -> List[Currency]:
        rates = self.fetch_exchange_rates()
        if not rates:
            logger.error("No rates fetched; skipping unofficial rate generation.")
            raise ValueError('No rates fetched')


        core_codes = set(self.core_currencies)  
        logger.debug(f'rates {rates}')
        logger.debug(f'core_codes {[str(code) for code in core_codes]}')

        converted_currencies = []
        currencies_dict = {currency.currencyCode: currency for currency in self.core_currencies}
        usd_currency = currencies_dict.get('USD')

        for currency in self.core_currencies:
            currencies_dict[currency.currencyCode] = currency

        usd_currency = currencies_dict.get('USD')

        for currency_code, rate_to_usd in rates.items():
            converted_buy_rate = usd_currency.buy / rate_to_usd
            converted_sell_rate = usd_currency.sell / rate_to_usd
            currency = Currency(
                currencyCode=currency_code,
                buy=converted_buy_rate,
                sell=converted_sell_rate,
                date=datetime.now().strftime("%Y-%m-%d"),
                is_core=False
            )
            converted_currencies.append(currency)
        final_currencies = [currency for currency in self.core_currencies + converted_currencies if not is_currency_excluded(currency.currencyCode)]

        logger.info("Generated unofficial rates for additional currencies.")
        return final_currencies

    def generate_official_rates(self) -> List[Currency]:
        """Generate or retrieve official currency exchange rates."""
        rates = self.fetch_exchange_rates()
        if not rates:
            logger.warning("No rates fetched; skipping official rate generation.")
            return []

        official_currencies = []
        for currency_code, rate in rates.items():
            if currency_code in {cur.currencyCode for cur in self.core_currencies}:
                currency = Currency(
                    currencyCode=currency_code,
                    buy=rate * 1.02,  # margin
                    sell=rate * 0.98,  # margin
                    date=datetime.now().strftime("%Y-%m-%d"),
                    is_core=True
                )
                official_currencies.append(currency)

        logger.info("Generated official rates for core currencies.")
        return official_currencies