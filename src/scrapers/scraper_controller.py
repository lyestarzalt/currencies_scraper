from typing import List, Type
from models.currency import Currency
from scrapers.base import CurrencyScraperBase
from scrapers.source_one_scraper import SourceOneScraper
from scrapers.source_two_scraper import SourceTwoScraper
from scrapers.source_three_scraper import SourceThreeScraper
from exceptions.data_exceptions import DataFetchError, DataParseError

class ScraperController:
    def __init__(self) -> None:
        # List scrapers by priority
        self.scrapers: List[Type[CurrencyScraperBase]] = [
            SourceThreeScraper,
            SourceOneScraper,
            SourceTwoScraper
        ]

    def fetch_currencies(self) -> List[Currency]:
        """
        Attempt to fetch currency data using each registered scraper in order of priority.
        Returns:
            List[Currency]: A list of parsed Currency instances if successful.
        Raises:
            Exception: If all scrapers fail to fetch and parse data.
        """
        for scraper_cls in self.scrapers:
            scraper = scraper_cls()
            try:
                print(f"Attempting to fetch data with {scraper.__class__.__name__}")
                currency_data = scraper.get_data()
                if currency_data:
                    print(f"Successfully fetched data with {scraper.__class__.__name__}")
                    return currency_data
            except (DataFetchError, DataParseError) as e:
                print(f"Failed to fetch data with {scraper.__class__.__name__}: {e}")
        raise Exception("All scrapers failed to fetch data.")
