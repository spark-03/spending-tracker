import streamlit as st
import json
import os
import datetime
import re
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

st.set_page_config(page_title="💸 Daily Spending Tracker", layout="centered")

st.markdown(
    """
    <style>
    body { font-family: 'Segoe UI', sans-serif; }
    .main { background-color: #f8f9fa; }
    .stApp { max-width: 700px; margin: auto; }
    .spend-card {
        background-color: #ffffff;
        padding: 1.2rem;
        margin: 1rem 0;
        border-radius: 1.2rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("💳 Gmail Spending Tracker")
st.caption("Powered by Gmail API · Built with ❤️ using Streamlit")

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# ----------------------------
# Authentication using token
# ----------------------------
def authenticate():
    token_dict = json.loads(st.secrets["token"]["token"])
    creds = Credentials.from_authorized_user_info(token_dict, SCOPES)
    return creds

# ----------------------------
# Fetch today's emails
# ----------------------------
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

# ----------------------------
# Extract ₹ amounts from messages
# ----------------------------
def extract_spending(service, messages):
    total = 0.0
    entries = []

    for msg in messages:
        try:
            data = service.users().messages().get(userId='me', id=msg['id']).execute()
            snippet = data.get('snippet', '')
            if any(k in snippet.lower() for k in ['debited', 'spent', 'purchase', 'payment']):
                match = re.search(r'(?:₹|INR|Rs\.?)\s?([\d,]+(?:\.\d{1,2})?)', snippet)
                if match:
                    amt = float(match.group(1).replace(',', ''))
                    total += amt
                    entries.append((amt, snippet[:70] + "..."))
        except Exception as e:
            continue
    return total, entries

# ----------------------------
# Run App
# ----------------------------
try:
    with st.spinner("🔐 Authenticating..."):
        creds = authenticate()
        service = build('gmail', 'v1', credentials=creds)

    with st.spinner("📬 Reading today’s emails..."):
        msgs = get_today_emails(service)
        total, txns = extract_spending(service, msgs)

    st.success("✅ Emails scanned successfully!")

    st.markdown(f"### 📅 Today's Total Spending: ₹{total:.2f}")

    for amt, desc in txns:
        st.markdown(
            f"<div class='spend-card'>"
            f"<b>₹{amt:.2f}</b><br><small>{desc}</small></div>",
            unsafe_allow_html=True,
        )

    if not txns:
        st.info("🎉 No spending detected today!")

except Exception as e:
    st.error(f"❌ Error: {e}")
