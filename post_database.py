import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from datetime import datetime
from scraper import DinarScraper


def lambda_handler(event, context):

    try:
        sr = DinarScraper()

        first_source = sr.get_forex_data()
        second_source = sr.get_devise_dz_data()

        # see who has the latest data
        if first_source[0] > second_source[0]:
            sell_dict = {
                currency.name: currency.sell for currency in first_source[1]}
            buy_dict = {
                currency.name: currency.buy for currency in first_source[1]}
        else:
            sell_dict = {
                currency.name: currency.sell for currency in second_source}
            buy_dict = {
                currency.name: currency.buy for currency in second_source}

        # upload the data to firebase
        cred = credentials.Certificate("exchange-dinar-key.json")
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        db.collection(u'exchange-daily').document(str(datetime.now().date())
                                                  ).set({"anis": [sell_dict, buy_dict]})

        return {
            'statusCode': 200,
            'body': 'Data updated successfully'
        }
    except Exception as e:
        print(e)
        return {
            'statusCode': 400,
            'body': f'An error occured'
        }


if __name__ == "__main__":
    lambda_handler(None, None)
