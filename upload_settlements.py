# upload_settlements.py
# This script uploads settlement transactions from a JSON file to Firebase Firestore.
import os
import firebase_admin
from firebase_admin import credentials, firestore
import json
import logging
from utils import validate_transaction, normalize_transaction

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

# Firebase Init
try:
    if os.getenv("FIRESTORE_EMULATOR_HOST"):
        os.environ["FIRESTORE_PROJECT_ID"] = "clearsettle-ai"
    if not firebase_admin._apps:  # Check if Firebase is already initialized
        cred = credentials.Certificate("/app/clearsettle-ai-firebase-adminsdk-fbsvc-844f7a5e30.json")
        firebase_admin.initialize_app(cred)
    db = firestore.client()
    logging.info("Firebase initialized successfully.")
except Exception as e:
    logging.error(f"Failed to initialize Firebase: {e}")
    exit()

def upload_to_database(transaction):
    try:
        collection_ref = db.collection('settlements')
        doc_ref = collection_ref.document(transaction['transaction_id'])
        doc_ref.set(transaction)
        logging.info(f"Transaction {transaction['transaction_id']} uploaded successfully.")
    except Exception as e:
        logging.error(f"Error uploading transaction {transaction['transaction_id']}: {e}")

def upload_transactions(transactions: list):
    seen_ids = set()
    for txn in transactions:
        txn = normalize_transaction(txn)
        if not validate_transaction(txn, seen_ids):
            logging.warning(f"Invalid or duplicate transaction skipped: {txn}")
            continue
        # Proceed with uploading the valid transaction
        upload_to_database(txn)

def main(data_file="/app/settlement_transactions.json"):
    try:
        with open(data_file, 'r') as f:
            transactions = json.load(f)
        logging.info(f"Loaded {len(transactions)} transactions from JSON file.")
    except Exception as e:
        logging.error(f"Failed to load transactions from JSON file: {e}")
        return

    logging.info("Uploading transactions...")
    upload_transactions(transactions)

if __name__ == "__main__":
    main()
