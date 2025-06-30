import os
import logging
import firebase_admin
from firebase_admin import credentials, firestore
import hashlib
import datetime

# Firebase Init
try:
    if not firebase_admin._apps:
        cred = credentials.Certificate("/app/clearsettle-ai-firebase-adminsdk-fbsvc-844f7a5e30.json")
        firebase_admin.initialize_app(cred)
    db = firestore.client()
except Exception as e:
    logging.error(f"Failed to initialize Firebase: {e}")
    exit()

def log_blockchain_activity():
    try:
        # Fetch settlement data
        docs = db.collection('settlements').stream()
        settlements = [doc.to_dict() for doc in docs]

        if not settlements:
            logging.warning("No settlements found for blockchain logging.")
            return

        # Debug: Log the fetched data
        logging.info(f"Fetched settlements: {len(settlements)} records")

        previous_hash = "0000"  # Genesis block
        for settlement in settlements:
            # Handle missing or mismatched transaction_id
            txn_id = settlement.get("transaction_id") or settlement.get("TransactionID")
            if not txn_id:
                logging.warning(f"Skipping settlement with missing transaction ID: {settlement}")
                continue

            action = f"Settlement status updated to '{settlement.get('SettlementStatus', 'unknown')}'"
            timestamp = datetime.datetime.utcnow().isoformat() + "Z"
            actor = "AI Engine"

            log_entry = {
                "transaction_id": txn_id,
                "timestamp": timestamp,
                "action": action,
                "actor": actor,
                "previous_hash": previous_hash
            }

            # Compute hash
            hash_input = (txn_id + timestamp + action + actor).encode()
            log_entry["hash"] = hashlib.sha256(hash_input).hexdigest()

            # Store in Firestore
            db.collection("audit_log").add(log_entry)
            previous_hash = log_entry["hash"]

        logging.info("Blockchain-style audit log created successfully.")
    except Exception as e:
        logging.error(f"Error during blockchain logging: {e}")

def main():
    log_blockchain_activity()
    logging.info("Blockchain logging completed.")

if __name__ == "__main__":
    main()
