import unittest
import requests_mock
from datetime import datetime, date
from scraper import DinarScraper, Currency


class TestDinarScraper(unittest.TestCase):
    """Basic test cases for DinarScraper class."""

    def test_get_forex_data(self):
        with requests_mock.Mocker() as mock:
            mock.post("http://www.forexalgerie.com/connect/updateExchange.php", json=[{
                "create_date_time": "07-02-2023 12:00:00",
                "eur_buy": "123.45",
                "eur_sell": "124.56",
                "usd_buy": "112.34",
                "usd_sell": "113.45"
            }])
            ds = DinarScraper()
            result = ds.get_forex_data()
            self.assertIsInstance(result, tuple)
            self.assertEqual(len(result), 2)
            self.assertIsInstance(result[0], datetime)
            self.assertEqual(result[0].strftime(
                '%d-%m-%Y %H:%M:%S'), '07-02-2023 12:00:00')
            self.assertIsInstance(result[1], list)
            self.assertEqual(len(result[1]), 2)
            self.assertIsInstance(result[1][0], Currency)
            self.assertEqual(result[1][0].name, 'eur')
            self.assertEqual(result[1][0].buy, 123.45)
            self.assertEqual(result[1][0].sell, 124.56)
            self.assertIsInstance(result[1][1], Currency)
            self.assertEqual(result[1][1].name, 'usd')
            self.assertEqual(result[1][1].buy, 112.34)
            self.assertEqual(result[1][1].sell, 113.45)

    def test_get_devise_dz_data(self):
        with open("tests/devise_dz_response.html",  encoding='UTF-8') as file:
            html_content = file.read()

        with requests_mock.Mocker() as mock_for_requests:
            mock_for_requests.get('https://www.devise-dz.com/square-port-said-alger/',
                                  text=html_content)
            ds = DinarScraper()
            result = ds.get_devise_dz_data()
            self.assertIsInstance(result, tuple)
            self.assertGreater(len(result), 0)
            self.assertIsInstance(result[1], Currency)
            self.assertIsInstance(result[0], date)


if __name__ == '__main__':
    unittest.main()
