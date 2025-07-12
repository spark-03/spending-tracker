import os
import datetime
import base64
import re

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Scope: read-only access to Gmail
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate_gmail():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def get_today_emails(service):
    today = datetime.datetime.utcnow().date()
    query = f'after:{today}'

    results = service.users().messages().list(userId='me', q=query).execute()
    messages = results.get('messages', [])
    
    return messages

def extract_debit_amounts(service, messages):
    total_spent = 0.0
    transaction_list = []

    for msg in messages:
        msg_data = service.users().messages().get(userId='me', id=msg['id']).execute()
        snippet = msg_data.get('snippet', '')

        if any(keyword in snippet.lower() for keyword in ['debited', 'spent', 'purchase', 'payment']):
            match = re.search(r'₹\s?([\d,]+(?:\.\d{1,2})?)', snippet)
            if match:
                amount = float(match.group(1).replace(',', ''))
                total_spent += amount
                transaction_list.append((amount, snippet[:80]))

    return total_spent, transaction_list

def main():
    creds = authenticate_gmail()
    service = build('gmail', 'v1', credentials=creds)

    messages = get_today_emails(service)
    total, transactions = extract_debit_amounts(service, messages)

    print(f"Total spent today: ₹{total:.2f}")
    for amt, detail in transactions:
        print(f"→ ₹{amt:.2f} | {detail}...")

if __name__ == '__main__':
    main()
