import json


class CurrencyDataProvider:
    def __init__(self, json_file_path):
        self.json_file_path = json_file_path
        self.currency_details = self.load_currency_data_from_json()

    def load_currency_data_from_json(self):
        with open(self.json_file_path, 'r', encoding='utf-8') as file:
            countries_data = json.load(file)
            currency_details = {}
            for country in countries_data:
                if 'currencies' in country:  # Check if 'currencies' key exists
                    for currency in country['currencies']:
                        currency_code = currency['code']
                        currency_details[currency_code] = {
                            'name': currency['name'],
                            'symbol': currency['symbol'],
                            'flag': country['flag'],
                            'is_core': False  # Default value
                        }
            return currency_details

    def get_currency_details(self, currency_code):
        return self.currency_details.get(currency_code, None)
