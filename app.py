import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

# Access Firebase credentials from secrets
firebase_credentials = st.secrets["firebase_credentials"]

# Initialize Firebase Admin SDK
if not firebase_admin._apps:  # Prevent reinitialization in Streamlit's reruns
    cred = credentials.Certificate(firebase_credentials)
    firebase_admin.initialize_app(cred)

# Example: Access Firestore
db = firestore.client()

st.title("Streamlit App with Firebase")
st.write("Firebase initialized successfully!")

# Example Firestore query
docs = db.collection("example_collection").stream()
for doc in docs:
    st.write(f"{doc.id} => {doc.to_dict()}")
