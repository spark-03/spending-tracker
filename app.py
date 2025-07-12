import streamlit as st
from email_reader import authenticate_gmail, get_today_emails, extract_debit_amounts
import time

st.set_page_config(page_title="Spending Tracker", layout="centered")

st.title("📬 Email-Based Spending Tracker")
st.write("Tracks how much you've spent *today* based on Gmail debit messages.")

# Manual refresh button
if st.button("🔄 Refresh Now"):
    creds = authenticate_gmail()
    service = creds and authenticate_gmail()
    messages = get_today_emails(service)
    total, transactions = extract_debit_amounts(service, messages)
    st.session_state['total'] = total
    st.session_state['transactions'] = transactions
    st.session_state['last_updated'] = time.strftime("%H:%M:%S")

# Auto-refresh every 5 minutes
countdown = st.experimental_get_query_params().get('countdown', [300])[0]
st_autorefresh = st.experimental_rerun if int(countdown) == 0 else st.empty()

if 'total' not in st.session_state:
    st.session_state['total'] = 0.0
    st.session_state['transactions'] = []
    st.session_state['last_updated'] = "--"

st.markdown("### 💰 Total Spent Today:")
st.metric(label="", value=f"₹ {st.session_state['total']:.2f}")

st.markdown("### 📋 Transactions Today:")
for amt, detail in st.session_state['transactions']:
    st.write(f"₹{amt:.2f} — {detail}...")

st.caption(f"Last updated at {st.session_state['last_updated']} | Auto-refreshes every 5 min")
