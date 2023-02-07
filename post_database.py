import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from datetime import datetime
from scraper import DinarScraper


""" This script scrape the latest exchange rates for the Algerian Dinar
    It compares the data from two sources and prints the latest one
    
    Im using it to upload the data to firestore database.
"""


sr = DinarScraper()

first_source = sr.get_forex_data()
second_source = sr.get_devise_dz_data()

# see who has the latest data
if first_source[0] > second_source[0]:
    sellDict = {currency.name: currency.sell for currency in first_source[1]}
    buyDict = {currency.name: currency.buy for currency in first_source[1]}
else:
    sellDict = {currency.name: currency.sell for currency in second_source}
    buyDict = {currency.name: currency.buy for currency in second_source}

# upload the data to firebase
cred = credentials.Certificate("exchange-dinar-key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()
db.collection(u'exchange-daily').document(str(datetime)
                                          ).set({"anis": [sellDict, buyDict]})
