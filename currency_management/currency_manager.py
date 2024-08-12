import requests
from datetime import date
from typing import Dict, List
from models.currency import Currency
from utils.logger import get_logger
from utils.currency_exclusions import is_currency_excluded
from utils.config import API_BASE_URL

logger = get_logger("CurrencyManager")


class CurrencyManager:
    def __init__(self, base_currency: str, core_currencies: List[Currency]):
        self.base_currency: str = "usd"
        self.core_currencies: List[Currency] = core_currencies

    def fetch_exchange_rates(self) -> Dict[str, float]:
        """Fetch exchange rates for the base currency from an external API."""
        url = f"{API_BASE_URL}{self.base_currency}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            logger.info(f"Exchange rates fetched for {self.base_currency}.")

            return data["rates"]
        except requests.RequestException as e:
            logger.error(
                f"Failed to fetch exchange rates from {url}: {str(e)}", exc_info=True
            )
            raise ConnectionError(
                f"Unable to retrieve exchange rates from external API: {str(e)}"
            ) from e

    def generate_unofficial_rates(self) -> List[Currency]:
        try:
            rates = self.fetch_exchange_rates()
            if not rates:
                logger.error("No rates fetched; skipping unofficial rate generation.")
                raise ValueError("No rates fetched")

            core_codes = set(self.core_currencies)
            converted_currencies = []
            currencies_dict = {
                currency.currencyCode: currency for currency in self.core_currencies
            }
            usd_currency = currencies_dict.get("USD")

            for currency in self.core_currencies:
                currencies_dict[currency.currencyCode] = currency

            usd_currency = currencies_dict.get("USD")
            if usd_currency is not None:
                for currency_code, rate_to_usd in rates.items():
                    converted_buy_rate = usd_currency.buy / rate_to_usd
                    converted_sell_rate = usd_currency.sell / rate_to_usd
                    currency = Currency(
                        currencyCode=currency_code,
                        buy=converted_buy_rate,
                        sell=converted_sell_rate,
                        update_date=date.today(),
                        is_core=False,
                    )
                    converted_currencies.append(currency)
            final_currencies = [
                currency
                for currency in self.core_currencies + converted_currencies
                if not is_currency_excluded(currency.currencyCode)
            ]

            logger.info("Unofficial exchange rates generated successfully.")
            return final_currencies
        except Exception as e:
            logger.error(
                f"Failed to generate unofficial rates: {str(e)}", exc_info=True
            )
            raise RuntimeError("Error generating unofficial exchange rates.") from e


    def generate_official_rates(self) -> List[Currency]:
        """Generate or retrieve official currency exchange rates."""
        try:
            rates = self.fetch_exchange_rates()
            if not rates:
                logger.warning("No rates fetched; skipping official rate generation.")
                return []

            official_currencies = []

            # Margins for buy and sell rates
            buy_margin = 1.02  # 2% higher for buying rates
            sell_margin = 0.98  # 2% lower for selling rates

            # Define core currencies
            _core_currencies = {
                "CNY",
                "USD",
                "CHF",
                "TRY",
                "AED",
                "EUR",
                "CAD",
                "SAR",
                "GBP",
            }

            for currency_code, rate in rates.items():
                if (
                    currency_code != 'usd'
                ):  # Ensure it's not the base currency
                    is_core = currency_code in _core_currencies

                    buy_rate = (1 / rate) * buy_margin
                    sell_rate = (1 / rate) * sell_margin

                    currency = Currency(
                        currencyCode=currency_code,
                        buy=buy_rate,
                        sell=sell_rate,
                        update_date=date.today(),
                        is_core=is_core,
                    )
                    official_currencies.append(currency)

            logger.info("Official exchange rates generated successfully.")
            return official_currencies

        except Exception as e:
            logger.warning(f"Failed to generate official rates: {str(e)}", exc_info=True)
            return []
