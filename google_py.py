import streamlit as st
import os, pickle
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# === SETTINGS ===
CLIENT_SECRET_FILE = "client_secret.json"  # Downloaded from Google Cloud
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# === FUNCTIONS ===
def get_credentials():
    creds = None
    # Load saved token if exists
    if os.path.exists("token.pkl"):
        with open("token.pkl", "rb") as token:
            creds = pickle.load(token)

    # Refresh if expired
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())

    # If no valid creds, start OAuth flow
    if not creds:
        flow = Flow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
        flow.redirect_uri = "http://localhost:8501"
        auth_url, _ = flow.authorization_url(prompt="consent")

        st.write(f"Please [Authorize Google Sheets Access]({auth_url})")
        st.stop()

    return creds


def connect_sheets(creds):
    """Return Google Sheets API client."""
    service = build("sheets", "v4", credentials=creds)
    return service.spreadsheets()


# === STREAMLIT UI ===
st.title("📊 Google Sheets Automation App")

try:
    creds = get_credentials()
    sheet_service = connect_sheets(creds)

    # User inputs Google Sheet link
    sheet_link = st.text_input("Enter Google Sheet link:")
    if sheet_link:
        try:
            # Extract Sheet ID
            SHEET_ID = sheet_link.split("/d/")[1].split("/")[0]
            RANGE = "Sheet1!A1:C10"  # Example range

            # Read values
            result = sheet_service.values().get(
                spreadsheetId=SHEET_ID, range=RANGE
            ).execute()
            values = result.get("values", [])

            st.subheader("Sheet Data:")
            st.write(values)

            # Example: Append data
            if st.button("Add Sample Row"):
                new_row = [["Hello", "from", "Streamlit"]]
                sheet_service.values().append(
                    spreadsheetId=SHEET_ID,
                    range="Sheet1!A1",
                    valueInputOption="RAW",
                    body={"values": new_row},
                ).execute()
                st.success("Row added!")

        except Exception as e:
            st.error(f"Error: {e}")

except Exception as e:
    st.error(f"Auth Error: {e}")
