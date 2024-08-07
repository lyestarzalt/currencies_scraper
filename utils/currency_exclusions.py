from utils.config import EXCLUDED_CURRENCIES

def get_excluded_currencies():
    return set(EXCLUDED_CURRENCIES)

def is_currency_excluded(currency_code: str) -> bool:
    """
    Check if a currency is in the excluded list.
    """
    excluded_currencies = get_excluded_currencies()
    return currency_code in excluded_currencies
