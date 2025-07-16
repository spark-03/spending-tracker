import base64
import re
from google.auth.transport.requests import Request

import streamlit as st
from datetime import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_credentials_from_secrets():
    secrets = st.secrets["google"]

    creds = Credentials(
        token=None,
        refresh_token=secrets["refresh_token"],
        token_uri=secrets["token_uri"],
        client_id=secrets["client_id"],
        client_secret=secrets["client_secret"],
        scopes=['https://www.googleapis.com/auth/gmail.readonly']
    )

    creds.refresh(Request())
    return creds

def extract_amount(text):
    # Match INR, Rs, ₹ followed by numbers (with optional commas and decimals)
    match = re.search(r'(?:INR|₹|Rs\.?)\s?([\d,]+(?:\.\d{1,2})?)', text, re.IGNORECASE)
    if match:
        try:
            amount_str = match.group(1).replace(',', '')
            return float(amount_str)
        except:
            return None
    return None

def extract_purpose(text):
    match = re.search(r'(paid to|payment to|sent to|debited for|for|towards|UPI.*?@.*?|POS/[\w\s]+).{0,40}', text, re.IGNORECASE)
    if match:
        return match.group().strip()
    return "Unknown"

def get_today_spending():
    creds = get_credentials_from_secrets()
    service = build('gmail', 'v1', credentials=creds)

    today = datetime.now().date()
    query = "subject:debited newer_than:1d"

    result = service.users().messages().list(userId='me', q=query).execute()
    messages = result.get('messages', [])

    transactions = []

    for msg in messages:
        msg_data = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()

        headers = msg_data['payload']['headers']
        date_str = next((h['value'] for h in headers if h['name'] == 'Date'), None)
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "No Subject")

        try:
            msg_time = datetime.strptime(date_str[:25], '%a, %d %b %Y %H:%M:%S')
        except Exception:
            continue

        if msg_time.date() != today:
            continue

        payload = msg_data['payload']
        text = ''
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain' and 'data' in part['body']:
                    text = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
                    break
        elif 'body' in payload and 'data' in payload['body']:
            text = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8', errors='ignore')

        amt = extract_amount(text)
        if amt:
            purpose = extract_purpose(text)
            transactions.append({
                'time': msg_time.strftime("%H:%M"),
                'amount': amt,
                'purpose': purpose,
                'subject': subject
            })

    return transactions
