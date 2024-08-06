import os
import firebase_admin
from firebase_admin import credentials, firestore

# Set the environment variable for Firestore emulator
os.environ["FIRESTORE_EMULATOR_HOST"] = "127.0.0.1:8080"

# Initialize Firebase Admin without a real credentials file
firebase_admin.initialize_app(options={
    'projectId': 'exchange-dinar-staging'
})

db = firestore.client()

# Function to list all collections
def list_collections():
    collections = db.collections()
    for collection in collections:
        print(collection.id)  # `id` attribute to get the name of the collection

# Fetch and print data from 'test' collection
test_ref = db.collection("test")
docs = test_ref.stream()
for doc in docs:
    print(f"{doc.id} => {doc.to_dict()}")

# List all collections
list_collections()
