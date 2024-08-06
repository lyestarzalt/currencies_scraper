from dataclasses import dataclass, field
from typing import Optional
import json
from datetime import datetime, date
from utils.logger import get_logger

logger = get_logger('CurrencyModel')

# Load the country data and prepare the currency map
try:
    with open("countries.json", "r") as file:
        countries = json.load(file)
    currency_map = {}
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
    name: str = ""
    symbol: str = ""
    flag: str = ""

    def __post_init__(self):
        currency_info = currency_map.get(self.currencyCode, {})
        self.name = currency_info.get("name", self.name)
        self.symbol = currency_info.get("symbol", self.symbol)
        self.flag = currency_info.get("flag", self.flag)
        if not self.update_date:
            self.update_date = datetime.now().strftime("%Y-%m-%d")
    def __eq__(self, other):
        if not isinstance(other, Currency):
            return NotImplemented
        return self.currencyCode == other.currencyCode

    def __hash__(self):
        return hash(self.currencyCode)

    def __str__(self):
        return f"{self.currencyCode}: {self.buy}/{self.sell} ({self.name})"
