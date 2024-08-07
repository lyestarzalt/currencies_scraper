class DataFetchError(Exception):
    """Exception raised when there is a problem fetching data from the source."""
    pass

class DataParseError(Exception):
    """Exception raised when there is a problem parsing the data."""
    pass
