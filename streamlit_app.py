import streamlit as st
import logging
from main_pipeline import run_pipeline

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

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
