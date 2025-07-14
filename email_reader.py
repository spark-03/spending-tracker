import datetime
import re
import streamlit as st
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Gmail API scope
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate_gmail():
    """
    Authenticate using credentials from Streamlit secrets.toml.
    """
    creds = Credentials(
        token=st.secrets["token"]["token"],
        refresh_token=st.secrets["token"]["refresh_token"],
        token_uri=st.secrets["token"]["token_uri"],
        client_id=st.secrets["token"]["client_id"],
        client_secret=st.secrets["token"]["client_secret"],
        scopes=SCOPES
    )
    return creds

def get_today_emails(service):
    """
    Fetches emails from today using Gmail API.
    """
    today = datetime.datetime.utcnow().date()
    query = f'after:{today.strftime("%Y/%m/%d")}'
    messages = []
    next_page_token = None

    while True:
        response = service.users().messages().list(
            userId='me', q=query, pageToken=next_page_token
        ).execute()

        messages.extend(response.get('messages', []))
        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break

    return messages

def extract_debit_amounts(service, messages):
    """
    Extracts all ₹ (rupee) amounts from Gmail snippets that mention spending keywords.
    Returns total spending and a list of (amount, description).
    """
    total_spent = 0.0
    transaction_list = []

    for msg in messages:
        try:
            msg_data = service.users().messages().get(userId='me', id=msg['id']).execute()
            snippet = msg_data.get('snippet', '')

            if any(keyword in snippet.lower() for keyword in ['debited', 'spent', 'purchase', 'payment']):
                match = re.search(r'(?:₹|INR|Rs\.?)\s?([\d,]+(?:\.\d{1,2})?)', snippet)
                if match:
                    amount = float(match.group(1).replace(',', ''))
                    total_spent += amount
                    transaction_list.append((amount, snippet[:80]))
        except Exception:
            continue

    return total_spent, transaction_list
