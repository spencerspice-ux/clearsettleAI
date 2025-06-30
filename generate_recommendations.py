# generate_recommendations.py
# This script generates recommendations based on root cause tags in Firebase Firestore.
# -*- coding: utf-8 -*-

import os
import logging
import firebase_admin
from firebase_admin import credentials, firestore

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

# Firebase Init
try:
    if not firebase_admin._apps:  # Check if Firebase is already initialized
        cred = credentials.Certificate("/app/clearsettle-ai-firebase-adminsdk-fbsvc-844f7a5e30.json")
        firebase_admin.initialize_app(cred)
    db = firestore.client()
    logging.info("Firebase initialized successfully.")
except Exception as e:
    logging.error(f"Failed to initialize Firebase: {e}")
    exit()

def generate_recommendations():
    try:
        # Fetch settlement data
        docs = db.collection('settlements').stream()
        recommendation_map = {
            "Insufficient securities": "Initiate securities recall",
            "Counterparty liquidity issue": "Request liquidity injection from counterparty",
            "Settlement window mismatch": "Initiate trade matching earlier",
            "anomaly_detected": "Investigate unusual settlement pattern",
            "normal": "Follow standard repair process – pattern is common"
        }

        updated_count = 0
        for doc in docs:
            data = doc.to_dict()
            tag = data.get("root_cause_tag", "")
            recommendation = recommendation_map.get(tag, "Investigate manually")

            # Update Firestore with the recommendation
            db.collection('settlements').document(doc.id).update({
                "recommendation": recommendation
            })
            updated_count += 1

        logging.info(f"Recommendations updated for {updated_count} transactions.")
        return updated_count
    except Exception as e:
        logging.error(f"Error generating recommendations: {e}")
        return 0

def main():
    recommendations = generate_recommendations()
    logging.info(f"Generated recommendations for {recommendations} transactions.")

if __name__ == "__main__":
    main()
