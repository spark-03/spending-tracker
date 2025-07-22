from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

def fetch_recent_messages(creds, query="debit", max_results=10):
    service = build("gmail", "v1", credentials=creds)
    result = service.users().messages().list(userId="me", q=query, maxResults=max_results).execute()
    messages = result.get("messages", [])

    email_contents = []

    for msg in messages:
        msg_data = service.users().messages().get(userId="me", id=msg["id"], format="full").execute()
        for part in msg_data["payload"].get("parts", []):
            if part["mimeType"] == "text/plain":
                data = part["body"]["data"]
                import base64
                decoded = base64.urlsafe_b64decode(data.encode("UTF-8")).decode("utf-8")
                email_contents.append(decoded)
                break
    return email_contents
