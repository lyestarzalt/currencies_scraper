from typing import Set
from utils.config import EXCLUDED_CURRENCIES

def get_excluded_currencies() -> Set[str]:
    """
    Get the set of excluded currencies from the configuration.
    
    Returns:
        Set[str]: A set of excluded currency codes.
    """
    return set(EXCLUDED_CURRENCIES)

def is_currency_excluded(currency_code: str) -> bool:
    """
    Check if a currency is in the excluded list.
    Args:
        currency_code (str): The currency code to check.

    Returns:
        bool: True if the currency is excluded, False otherwise.
    """
    excluded_currencies = get_excluded_currencies()
    return currency_code in excluded_currencies
