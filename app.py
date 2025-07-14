import streamlit as st
from email_reader import authenticate_gmail, get_today_emails, extract_debit_amounts
from googleapiclient.discovery import build
import time

st.set_page_config(page_title="Spending Tracker", layout="centered")

st.title("📬 Email-Based Spending Tracker")
st.write("Tracks how much you've spent *today* based on Gmail debit messages.")

# Manual refresh button
if st.button("🔄 Refresh Now"):
    creds = authenticate_gmail()
    service = build('gmail', 'v1', credentials=creds)
    messages = get_today_emails(service)
    total, transactions = extract_debit_amounts(service, messages)
    st.session_state['total'] = total
    st.session_state['transactions'] = transactions
    st.session_state['last_updated'] = time.strftime("%H:%M:%S")

# Initialize state
if 'total' not in st.session_state:
    st.session_state['total'] = 0.0
    st.session_state['transactions'] = []
    st.session_state['last_updated'] = "--"

# Display results
st.markdown("### 💰 Total Spent Today:")
st.metric(label="", value=f"₹ {st.session_state['total']:.2f}")

st.markdown("### 📋 Transactions Today:")
if st.session_state['transactions']:
    for amt, detail in st.session_state['transactions']:
        st.write(f"₹{amt:.2f} — {detail}...")
else:
    st.info("No debit transactions found today.")

st.caption(f"Last updated at {st.session_state['last_updated']} | Click refresh to update.")
