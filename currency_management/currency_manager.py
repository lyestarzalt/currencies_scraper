import requests
from datetime import date, datetime
from typing import Dict, List
from models.currency import Currency
from utils.logger import get_logger
from utils.currency_exclusions import is_currency_excluded
from utils.config import API_BASE_URL

logger = get_logger("CurrencyManager")


class CurrencyManager:
    def __init__(self, core_currencies: List[Currency]):
        self.core_currencies: List[Currency] = core_currencies

    def fetch_exchange_rates(self, base_currency: str) -> Dict[str, float]:
        """Fetch exchange rates for the base currency from an external API."""
        url = f"{API_BASE_URL}{base_currency}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            logger.info(f"Exchange rates fetched for {base_currency}.")

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
            rates = self.fetch_exchange_rates("usd")
            if not rates:
                logger.error("No rates fetched; skipping unofficial rate generation.")
                raise ValueError("No rates fetched")

            core_currency_codes = {
                currency.currencyCode for currency in self.core_currencies
            }

            converted_currencies = []
            usd_currency = next(
                (
                    currency
                    for currency in self.core_currencies
                    if currency.currencyCode == "USD"
                ),
                None,
            )

            if usd_currency is not None:
                for currency_code, rate_to_usd in rates.items():
                    # Skip if this currency is a core currency
                    if currency_code in core_currency_codes:
                        continue

                    converted_buy_rate = usd_currency.buy / rate_to_usd
                    converted_sell_rate = usd_currency.sell / rate_to_usd

                    currency = Currency(
                        currencyCode=currency_code,
                        buy=converted_buy_rate,
                        sell=converted_sell_rate,
                        update_date=date.today().strftime("%Y-%m-%d"),
                        is_core=False,
                    )
                    converted_currencies.append(currency)

            # Combine the core and converted currencies first
            combined_currencies = self.core_currencies + converted_currencies

            # Filter out excluded currencies from the combined list
            final_currencies = [
                currency for currency in combined_currencies
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
        """Generate or retrieve official currency exchange rates based on DZD."""
        try:
            rates = self.fetch_exchange_rates("DZD")
            if not rates:
                logger.warning("No rates fetched; skipping official rate generation.")
                return []

            official_currencies = []
            buy_margin = 1.02  # 2% higher for buying rates
            sell_margin = 0.98  # 2% lower for selling rates
            core_currencies = {
                "EUR",
                "USD",
                "GBP",
                "CAD",
                "CHF",
                "TRY",
                "SAR",
                "CNY",
                "AED",
            }

            for currency_code, rate in rates.items():
                if currency_code != "DZD":
                    is_core = currency_code in core_currencies
                    buy_rate = (1 / rate) * buy_margin
                    sell_rate = (1 / rate) * sell_margin

                    currency = Currency(
                        currencyCode=currency_code,
                        buy=buy_rate,
                        sell=sell_rate,
                        update_date=date.today().strftime("%Y-%m-%d"),
                        is_core=is_core,
                    )
                    official_currencies.append(currency)

            final_currencies = [
                currency
                for currency in official_currencies
                if not is_currency_excluded(currency.currencyCode)
            ]

            logger.info("Unofficial exchange rates generated successfully.")
            return final_currencies

        except Exception as e:
            logger.warning(
                f"Failed to generate official rates: {str(e)}", exc_info=True
            )
            raise RuntimeError("Error generating official exchange rates.") from e
