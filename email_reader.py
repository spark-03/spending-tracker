import os
import sys
sys.path.append(r"C:\Users\91636\AppData\Roaming\Python\Python311\site-packages")
from google.auth.transport.requests import Request

import datetime
import base64
import re

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

# Scope: read-only access to Gmail
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate_gmail():
    creds = None
    token_path = "token.json"

    # Load saved token
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    # If no token or invalid, authenticate and save token
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for next run
        with open(token_path, 'w') as token_file:
            token_file.write(creds.to_json())

    return creds

def get_today_emails(service):
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

        except Exception as e:
            print(f"Failed to read a message: {e}")
            continue

    return total_spent, transaction_list

def main():
    creds = authenticate_gmail()
    service = build('gmail', 'v1', credentials=creds)

    messages = get_today_emails(service)
    total, transactions = extract_debit_amounts(service, messages)

    print(f"\n📅 TOTAL SPENT TODAY: ₹{total:.2f}\n")
    for amt, detail in transactions:
        print(f"→ ₹{amt:.2f} | {detail}...")

if __name__ == '__main__':
    main()
