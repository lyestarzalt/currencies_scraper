from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Tuple, Optional
from dataclasses import dataclass
from models.currency import Currency
import requests



class CurrencyScraperBase(ABC):
    """
    Base class for all currency scrapers
    """

    @abstractmethod
    def fetch_data(self, url: str) -> Optional[str]:
        """Fetch data from the given URL."""
        pass

    @abstractmethod
    def parse_data(self, html_content: str) -> Tuple[datetime, List[Currency]]:
        """Example: Parse the HTML content and return the date and list of Currency."""
        pass

    def get_data(self, url: str) -> Tuple[datetime, List[Currency]]:
        """Template method to fetch and parse data."""
        html_content = self.fetch_data(url)
        if html_content:
            return self.parse_data(html_content)
        else:
            return datetime.now(), []
