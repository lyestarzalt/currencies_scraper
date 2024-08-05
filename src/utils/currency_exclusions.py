import os

def get_excluded_currencies():
    excluded = os.getenv("EXCLUDED_CURRENCIES", "DZD,ILS")
    return set(excluded.split(","))

def is_currency_excluded(currency_code: str) -> bool:
    """
    Check if a currency is in the excluded list.
    """
    excluded_currencies = get_excluded_currencies()
    return currency_code in excluded_currencies
