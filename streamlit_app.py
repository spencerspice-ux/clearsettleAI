import streamlit as st
import logging
import firebase_admin
from firebase_admin import credentials, firestore
from main_pipeline import run_pipeline

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Access Firebase credentials from secrets
firebase_credentials = st.secrets["firebase_credentials"]

# Initialize Firebase Admin SDK
if not firebase_admin._apps:  # Prevent reinitialization in Streamlit's reruns
    cred = credentials.Certificate(firebase_credentials)  # Use secrets directly
    firebase_admin.initialize_app(cred)

# Streamlit App
st.title("ClearSettle AI Pipeline")
st.markdown("🚀 **Welcome to ClearSettle AI!** Use this app to process settlement transactions.")

# File uploader for settlement transactions
uploaded_file = st.file_uploader("Upload Settlement Transactions JSON File", type=["json"])

if st.button("Run Pipeline"):
    if uploaded_file:
        # Save uploaded file temporarily
        with open("uploaded_transactions.json", "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        st.info("📤 Starting the pipeline...")
        try:
            run_pipeline(data_file="uploaded_transactions.json")
            st.success("🏁 Pipeline completed successfully!")
        except Exception as e:
            st.error(f"❌ An error occurred: {e}")
    else:
        st.warning("⚠️ Please upload a JSON file to proceed.")
