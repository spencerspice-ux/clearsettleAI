import os
import logging
import firebase_admin
from firebase_admin import credentials, firestore
from sklearn.ensemble import IsolationForest
import pandas as pd
from utils import validate_transaction, normalize_status, normalize_field, normalize_transaction
from logging.handlers import RotatingFileHandler
from tenacity import retry, stop_after_attempt, wait_exponential
from autoencoder_model import detect_anomalies_with_autoencoder
from tensorflow.keras.models import load_model
from sklearn.preprocessing import StandardScaler
import numpy as np

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Configure logging to write to a file and console
log_file = "logs/app.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),  # Log to console
        RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=3)  # Log to file with rotation
    ]
)

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

@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=2, max=10))
def update_firestore_with_retry(doc_ref, data):
    """
    Update Firestore document with retry logic.

    Args:
        doc_ref: Firestore document reference.
        data: Data to update in the document.
    """
    doc_ref.update(data)

def process_anomalies(valid_transactions):
    try:
        # Convert transactions to a DataFrame
        df = pd.DataFrame(valid_transactions)

        if df.empty:
            logging.warning("No valid settlement data found.")
            return []

        # Prepare data for anomaly detection
        features = df[['anomaly_score']].fillna(0)

        # Fine-tuned Isolation Forest model
        model = IsolationForest(
            n_estimators=200,        # More trees for stability
            contamination=0.02,      # Adjust based on expected anomaly proportion
            max_features=0.8,        # Avoid overfitting on small fields
            random_state=42
        )
        df['anomaly'] = model.fit_predict(features)

        # Log model performance
        logging.info(f"Anomaly Score Threshold: {model.offset_}")
        anomalies = df[df['anomaly'] == -1]
        logging.info(f"Anomalies Detected: {len(anomalies)} out of {len(df)} transactions")

        # Update Firestore with anomaly detection results
        for _, row in anomalies.iterrows():
            doc_ref = db.collection('settlements').document(row['transaction_id'])
            update_firestore_with_retry(doc_ref, {'anomaly_detected': True})

        # Export anomalies to a CSV file
        if not anomalies.empty:
            anomalies.to_csv("logs/anomalies.csv", index=False)
            logging.info("Anomalies exported to logs/anomalies.csv")

        return anomalies['transaction_id'].tolist()
    except Exception as e:
        logging.error(f"Error during anomaly detection: {e}")
        return []

def process_anomalies_with_autoencoder(valid_transactions):
    """
    Detect anomalies using the Autoencoder.

    Args:
        valid_transactions (list): List of valid transactions.

    Returns:
        list: List of anomalies detected.
    """
    try:
        # Convert transactions to a DataFrame
        df = pd.DataFrame(valid_transactions)

        if df.empty:
            logging.warning("No valid settlement data found.")
            return []

        # Load the trained Autoencoder model and scaler
        model = load_model("autoencoder_model.keras")
        scaler = StandardScaler()
        scaler.fit(df)  # Ensure the scaler is consistent with training

        # Detect anomalies
        threshold = 0.01  # Set a threshold for reconstruction error
        anomalies = detect_anomalies_with_autoencoder(df.values, model, scaler, threshold)

        # Log anomalies
        anomaly_indices = np.where(anomalies)[0]
        logging.info(f"Anomalies Detected: {len(anomaly_indices)} out of {len(df)} transactions")

        # Update Firestore with anomaly detection results
        for idx in anomaly_indices:
            txn = valid_transactions[idx]
            doc_ref = db.collection('settlements').document(txn['transaction_id'])
            update_firestore_with_retry(doc_ref, {'anomaly_detected': True})

        # Export anomalies to a CSV file
        anomalies_df = df.iloc[anomaly_indices]
        if not anomalies_df.empty:
            anomalies_df.to_csv("logs/anomalies_autoencoder.csv", index=False)
            logging.info("Anomalies exported to logs/anomalies_autoencoder.csv")

        return anomalies_df['transaction_id'].tolist()
    except Exception as e:
        logging.error(f"Error during anomaly detection with Autoencoder: {e}")
        return []

def detect_anomalies(transactions: list):
    """
    Detect anomalies in the given transactions.

    Args:
        transactions (list): List of transaction dictionaries.

    Returns:
        list: List of anomalies detected.
    """
    seen_ids = set()
    normalized_transactions = [normalize_transaction(txn) for txn in transactions]
    valid_transactions = [txn for txn in normalized_transactions if validate_transaction(txn, seen_ids)]
    
    if len(valid_transactions) < len(transactions):
        logging.warning("Some invalid or duplicate transactions were skipped during anomaly detection.")
    
    return process_anomalies(valid_transactions)

def main():
    try:
        # Fetch settlement data
        docs = db.collection('settlements').stream()
        transactions = [doc.to_dict() for doc in docs]

        if not transactions:
            logging.warning("No settlement data found.")
            return

        # Detect anomalies using IsolationForest
        anomalies = detect_anomalies(transactions)
        logging.info(f"Detected {len(anomalies)} anomalies using IsolationForest.")

        # Detect anomalies using Autoencoder
        autoencoder_anomalies = process_anomalies_with_autoencoder(transactions)
        logging.info(f"Detected {len(autoencoder_anomalies)} anomalies using Autoencoder.")
    except Exception as e:
        logging.error(f"Error in main: {e}")

if __name__ == "__main__":
    main()
