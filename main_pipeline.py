import logging
from upload_settlements import main as upload_settlements
from anomaly_detection import main as detect_anomalies
from generate_recommendations import main as generate_recommendations
from simulate_blockchain_log import main as log_blockchain_activity

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def run_pipeline(data_file="/app/settlement_transactions.json"):
    logging.info("🚀 Starting ClearSettle AI pipeline...")

    # Step 1: Upload Settlements
    logging.info("📤 Step 1: Uploading settlements...")
    try:
        upload_settlements(data_file)
        logging.info("✅ Settlements uploaded successfully.")
    except Exception as e:
        logging.error(f"❌ Error uploading settlements: {e}")
        return

    # Step 2: Anomaly Detection
    logging.info("⚠️ Step 2: Running anomaly detection...")
    try:
        detect_anomalies()
        logging.info("✅ Anomaly detection completed.")
    except Exception as e:
        logging.error(f"❌ Error during anomaly detection: {e}")
        return

    # Step 3: Generate Recommendations
    logging.info("🎯 Step 3: Generating recommendations...")
    try:
        generate_recommendations()
        logging.info("✅ Recommendations generated successfully.")
    except Exception as e:
        logging.error(f"❌ Error generating recommendations: {e}")
        return

    # Step 4: Blockchain-style Logging
    logging.info("🔐 Step 4: Simulating blockchain logs...")
    try:
        log_blockchain_activity()
        logging.info("✅ Blockchain logs updated successfully.")
    except Exception as e:
        logging.error(f"❌ Error during blockchain logging: {e}")
        return

    logging.info("🏁 Pipeline completed successfully.\n")

if __name__ == "__main__":
    run_pipeline()