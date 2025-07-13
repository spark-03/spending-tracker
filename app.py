import streamlit as st
from email_reader import authenticate_gmail, get_today_emails, extract_debit_amounts
from googleapiclient.discovery import build
import datetime

# --- Streamlit Page Setup ---
st.set_page_config(page_title="💸 Spending Tracker", layout="centered")

# --- Inject Custom CSS for Styling ---
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .title {
        font-size: 2.5em;
        color: #222831;
        text-align: center;
        font-weight: 700;
    }
    .subtitle {
        font-size: 1.2em;
        color: #393E46;
        text-align: center;
        margin-bottom: 30px;
    }
    .card {
        background-color: white;
        padding: 1.5em;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .amount {
        font-size: 2em;
        font-weight: bold;
        color: #00ADB5;
    }
    .footer {
        font-size: 0.9em;
        text-align: center;
        color: #666;
        margin-top: 50px;
    }
    </style>
""", unsafe_allow_html=True)

# --- Title & Info ---
st.markdown('<div class="title">💳 Gmail Spending Tracker</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Auto-fetch debit alerts from Gmail & calculate today\'s spending</div>', unsafe_allow_html=True)

# --- Session State Setup ---
if "last_refreshed" not in st.session_state:
    st.session_state["last_refreshed"] = None
    st.session_state["transactions"] = []
    st.session_state["total_spent"] = 0.0

# --- Refresh Button ---
if st.button("🔄 Refresh Now"):
    try:
        creds = authenticate_gmail()
        service = build('gmail', 'v1', credentials=creds)
        messages = get_today_emails(service)
        total, transactions = extract_debit_amounts(service, messages)

        st.session_state["total_spent"] = total
        st.session_state["transactions"] = transactions
        st.session_state["last_refreshed"] = datetime.datetime.now()

        st.success("✅ Refreshed successfully!")
    except Exception as e:
        st.error(f"❌ Error while fetching Gmail data:\n{e}")

# --- Spending Card ---
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown("#### 📅 Today's Total Spent")
st.markdown(f'<div class="amount">₹{st.session_state["total_spent"]:.2f}</div>', unsafe_allow_html=True)
if st.session_state["last_refreshed"]:
    st.caption(f"Last updated: {st.session_state['last_refreshed'].strftime('%I:%M:%S %p')}")
st.markdown('</div>', unsafe_allow_html=True)

# --- Transactions ---
if st.session_state["transactions"]:
    st.markdown('<div class="card"><h4>🧾 Transactions</h4>', unsafe_allow_html=True)
    for amt, detail in st.session_state["transactions"]:
        st.markdown(f"<p>→ <strong>₹{amt:.2f}</strong> — {detail}...</p>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.info("No debit transactions found for today.")

# --- Footer ---
st.markdown('<div class="footer">🔐 Your Gmail data is processed securely via OAuth. Nothing is stored.</div>', unsafe_allow_html=True)
