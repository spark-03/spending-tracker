import base64
import os
import re
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta


# Load Gmail API credentials from a service account
def get_gmail_service():
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    SERVICE_ACCOUNT_FILE = 'secrets/service_account.json'  # Replace with your file path

    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    delegated_creds = credentials.with_subject('your-email@gmail.com')  # replace with your Gmail
    service = build('gmail', 'v1', credentials=delegated_creds)
    return service


# Fetch emails from the last N days that contain keywords related to debits
def fetch_debit_emails(days=30):
    service = get_gmail_service()
    user_id = 'me'
    query = 'subject:debited OR subject:withdrawal OR "Rs." after:' + \
            (datetime.now() - timedelta(days=days)).strftime('%Y/%m/%d')

    results = service.users().messages().list(userId=user_id, q=query).execute()
    messages = results.get('messages', [])
    
    debit_list = []

    for msg in messages:
        txt = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
        payload = txt['payload']
        headers = payload.get('headers', [])

        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
        date = next((h['value'] for h in headers if h['name'] == 'Date'), '')

        parts = payload.get('parts', [])
        body = ""

        for part in parts:
            if part['mimeType'] == 'text/plain':
                data = part['body']['data']
                body = base64.urlsafe_b64decode(data).decode('utf-8')
                break

        # Very basic debit detection logic
        match = re.search(r'Rs\.?\s?([\d,]+\.\d{2})', body)
        if match:
            amount = match.group(1).replace(",", "")
            debit_list.append({
                'date': date,
                'subject': subject,
                'amount': float(amount)
            })

    return debit_list
