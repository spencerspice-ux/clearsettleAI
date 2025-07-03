# clearsettleAI

## Setup Instructions

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Firebase Credentials**:
   - Place your Firebase Admin SDK JSON file in the project root.
   - Update the `GOOGLE_APPLICATION_CREDENTIALS` environment variable in `docker-compose.yml`.

3. **Run Pipeline**:
   ```bash
   python main_pipeline.py
   ```

4. **Streamlit App**:
   - Start the Streamlit app:
     ```bash
     streamlit run streamlit_app.py
     ```
   - Access the app at `http://localhost:8501`.