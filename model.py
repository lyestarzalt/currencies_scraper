
from dataclasses import dataclass


@dataclass
class Currency:
    currencyCode: str = None
    name: str = None
    symbol: str = None
    flag: str = None
    buy: float = None
    sell: float = None
    date: str = None
    is_core: bool = False
