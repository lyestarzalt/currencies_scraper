from dataclasses import dataclass, field
from typing import Optional, Dict, Any
import json
from datetime import datetime, date
from utils.logger import get_logger

logger = get_logger("CurrencyModel")

try:
    with open("countries.json", "r") as file:
        countries = json.load(file)
    currency_map: Dict[str, Dict[str, Any]] = {}
    for country in countries:
        if "currencies" in country:
            for currency in country["currencies"]:
                currency_map[currency["code"]] = {
                    "symbol": currency["symbol"],
                    "name": currency["name"],
                    "flag": country["flag"],
                }
    logger.info("Currency map successfully loaded from countries.json.")
except Exception as e:
    logger.error(f"Failed to load currency data: {e}")


@dataclass
class Currency:
    currencyCode: str
    buy: float
    sell: float
    is_core: bool
    update_date: date
    name: str = field(default="")
    symbol: str = field(default="")
    flag: str = field(default="")

    def __post_init__(self) -> None:
        """
        Initialize additional attributes for the currency instance.
        """
        currency_info = currency_map.get(self.currencyCode, {})
        self.name = currency_info.get("name", self.name)
        self.symbol = currency_info.get("symbol", self.symbol)
        self.flag = currency_info.get("flag", self.flag)
        if not self.update_date:
            self.update_date = datetime.now().date()

    def __eq__(self, other: object) -> bool:
        """
        Check equality based on the currency code.

        Args:
            other (object): Another instance to compare with.

        Returns:
            bool: True if the currency codes are equal, False otherwise.
        """
        if not isinstance(other, Currency):
            return NotImplemented
        return self.currencyCode == other.currencyCode

    def __hash__(self) -> int:
        """
        Return a hash based on the currency code.

        Returns:
            int: The hash value of the currency code.
        """
        return hash(self.currencyCode)

    def __str__(self) -> str:
        """
        Return a string representation of the currency instance.

        Returns:
            str: A string representing the currency.
        """
        return f"{self.currencyCode}: {self.buy}/{self.sell} ({self.name})"
