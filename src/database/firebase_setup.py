from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore



def create_or_update_document():
    """Creates or updates a document in the 'test' collection."""
    cred_path = 'exchange-dinar-staging-firebase-adminsdk.json'
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)

    db = firestore.client()
    db.collection(
            u'test').document('testsafd').set({"hello":"workd"})


if __name__ == "__main__":
    create_or_update_document()
