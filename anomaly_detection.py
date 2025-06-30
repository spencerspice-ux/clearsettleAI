import os  # Add this import
import logging
import firebase_admin
from firebase_admin import credentials, firestore
from sklearn.ensemble import IsolationForest
import pandas as pd

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

def detect_anomalies():
    try:
        # Fetch settlement data
        docs = db.collection('settlements').stream()
        data = [doc.to_dict() for doc in docs]
        df = pd.DataFrame(data)

        if df.empty:
            logging.warning("No settlement data found.")
            return []

        # Prepare data for anomaly detection
        features = df[['anomaly_score']].fillna(0)
        model = IsolationForest(contamination=0.1, random_state=42)
        df['anomaly'] = model.fit_predict(features)

        # Update Firestore with anomaly detection results
        anomalies = []
        for index, row in df.iterrows():
            if row['anomaly'] == -1:  # Anomaly detected
                anomalies.append(row['transaction_id'])
                db.collection('settlements').document(row['transaction_id']).update({
                    'anomaly_detected': True
                })

        logging.info(f"Anomalies detected: {len(anomalies)}")
        return anomalies
    except Exception as e:
        logging.error(f"Error during anomaly detection: {e}")
        return []

def main():
    anomalies = detect_anomalies()
    logging.info(f"Detected {len(anomalies)} anomalies.")

if __name__ == "__main__":
    main()
