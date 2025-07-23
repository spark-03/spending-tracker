import base64
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from utils.email_fetcher import extract_debit_amounts


def fetch_debit_emails(user_credentials: dict, max_results=50):
    """
    Fetches recent debit-related emails and extracts debit amounts.

    Args:
        user_credentials (dict): Authenticated credentials from session_state.
        max_results (int): Number of emails to scan.

    Returns:
        List of dicts: [{date, snippet, amount}]
    """
    creds = Credentials.from_authorized_user_info(user_credentials)
    service = build("gmail", "v1", credentials=creds)

    query = "subject:(debit OR transaction) -category:promotions"
    results = service.users().messages().list(userId="me", maxResults=max_results, q=query).execute()
    messages = results.get("messages", [])

    debit_data = []

    for msg in messages:
        msg_data = service.users().messages().get(userId="me", id=msg["id"], format="full").execute()
        headers = msg_data.get("payload", {}).get("headers", [])
        snippet = msg_data.get("snippet", "")

        # Extract email date
        date = next((h["value"] for h in headers if h["name"] == "Date"), "Unknown")

        # Try to get plain text body
        try:
            parts = msg_data["payload"].get("parts", [])
            for part in parts:
                if part["mimeType"] == "text/plain":
                    body_data = part["body"]["data"]
                    decoded_body = base64.urlsafe_b64decode(body_data).decode("utf-8")

                    amounts = extract_debit_amounts([decoded_body])
                    for amt in amounts:
                        debit_data.append({
                            "date": date,
                            "snippet": snippet,
                            "amount": amt
                        })
        except Exception:
            continue

    return debit_data
