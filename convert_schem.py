import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate('serviceAccountKey.json')
firebase_admin.initialize_app(cred)

db = firestore.client()


def convert_data():
    collection_ref = db.collection('exchange-daily')

    for doc in collection_ref.stream():
        doc_data = doc.to_dict()
        new_data = {}

        for currency_set in doc_data['anis']:
            for currency, value in currency_set.items():
                if currency not in new_data:
                    new_data[currency] = {}
                if 'buy' in new_data[currency]:
                    new_data[currency]['sell'] = value
                else:
                    new_data[currency]['buy'] = value

        doc.reference.set(new_data)


convert_data()
