
from scrapers.source_one_scraper import SourceOneScraper
from scrapers.source_two_scraper import SourceTwoScraper

def get_first_scraper():
    """Return the first configured scraper."""
    # Instantiate each scraper
    scrapers = [
        #SourceOneScraper(),
         SourceTwoScraper(),  # Uncomment or add additional scrapers as needed
    ]
    # Return the first scraper in the list
    return scrapers[0]

def run_first_scraper():
    """Run the first scraper and return its data."""
    scraper = get_first_scraper()
    scrape_time, currencies = scraper.get_data()
    print(f"Data from {scraper.__class__.__name__} at {scrape_time}: {currencies}")
    return scrape_time, currencies