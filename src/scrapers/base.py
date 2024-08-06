from abc import ABC, abstractmethod
from typing import List, Any
from models.currency import Currency
from exceptions.data_exceptions import DataFetchError, DataParseError
from utils.logger import get_logger

class CurrencyScraperBase(ABC):
    """
    Base class for all currency scrapers.

    Raises:
        DataFetchError: If there is an error in fetching data from the source.
        DataParseError: If there is an error in parsing the fetched data.
    """
    def __init__(self):
        # Initialize a logger for each specific scraper subclass.
        # The class name of the subclass will be used for logging.
        self.logger = get_logger(self.__class__.__name__)

    @abstractmethod
    def fetch_data(self) -> Any:
        """
        Fetch data from a pre-configured source.
        
        Returns:
            str: The content fetched from the data source.

        Raises:
            DataFetchError: If there is an error in fetching data.
        """
        pass

    @abstractmethod
    def parse_data(self, data_content: Any) -> List[Currency]:
        """
        Parse the fetched content to extract currency data.

        Args:
            data_content (str): The raw data content to be parsed.

        Returns:
            List[Currency]: A list of Currency instances parsed from the data content.

        Raises:
            DataParseError: If there is an error in parsing the data.
        """
        pass

    def get_data(self) -> List[Currency]:
        """ Template method to fetch and parse data. """
        self.logger.info("Initiating data retrieval process.")
        try:
            raw_data = self.fetch_data()
            if raw_data:
                currencies = self.parse_data(raw_data)
                if currencies:
                    self.logger.info(f"Successfully parsed {len(currencies)} currencies.")
                    return currencies
                else:
                    raise DataFetchError("No currencies parsed; possible data issues.")
        except DataFetchError as e:
            self.logger.error(f"Data processing failed: {e}")
            raise
        except DataParseError as e:
            self.logger.error(f"Parsing failed: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}", exc_info=True)
            raise DataFetchError("An unexpected error occurred during data processing.") from e
