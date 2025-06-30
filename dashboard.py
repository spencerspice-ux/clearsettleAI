import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
import logging

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

# Load Settlements Data
@st.cache_data
def load_settlements():
    try:
        docs = db.collection('settlements').stream()
        data = [doc.to_dict() | {"doc_id": doc.id} for doc in docs]
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Failed to load settlements: {e}")
        return pd.DataFrame()

# Load Audit Log Data
@st.cache_data
def load_audit_logs():
    try:
        logs = db.collection('audit_log').order_by('timestamp').stream()
        data = [doc.to_dict() for doc in logs]
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Failed to load audit logs: {e}")
        return pd.DataFrame()

# UI
st.set_page_config(layout="wide")
st.title("📊 ClearSettle AI – Settlement Dashboard")

settlements_df = load_settlements()
audit_df = load_audit_logs()

# Sidebar filter
status_filter = st.sidebar.multiselect("Filter by Status", options=["pending", "failed", "settled"], default=["failed"])
filtered_df = settlements_df[settlements_df["status"].isin(status_filter)].copy()

# Add the "Anomaly" column explicitly using .loc
filtered_df.loc[:, "Anomaly"] = filtered_df["root_cause_tag"].apply(lambda x: "⚠️" if x == "anomaly_detected" else "✅")

# Display Main Table
st.subheader(f"🧾 Settlement Overview ({len(filtered_df)} results)")
st.dataframe(
    filtered_df[[
        "transaction_id", "status", "asset_type", "isin_code",
        "counterparty_1", "counterparty_2",
        "anomaly_score", "root_cause_tag", "recommendation", "Anomaly"
    ]].sort_values("anomaly_score", ascending=False).reset_index(drop=True),
    use_container_width=True
)

# Audit Log Viewer
st.subheader("🧾 Blockchain-style Audit Log")

txn_ids = settlements_df["transaction_id"].unique().tolist()
selected_txn = st.selectbox("Select a Transaction ID to view audit history", txn_ids)

txn_logs = audit_df[audit_df["transaction_id"] == selected_txn]

if not txn_logs.empty:
    st.write(f"🔗 Showing {len(txn_logs)} audit blocks for `{selected_txn}`")
    st.dataframe(txn_logs[["timestamp", "action", "actor", "hash", "previous_hash"]], use_container_width=True)
else:
    st.info("No audit logs found for the selected transaction.")
