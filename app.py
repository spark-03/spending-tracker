import streamlit as st
from email_reader import authenticate_gmail, get_today_emails, extract_debit_amounts
from googleapiclient.discovery import build
import time

# Page config
st.set_page_config(page_title="Spending Tracker 💳", layout="centered")

# Custom styling with black font
st.markdown("""
    <style>
        .stApp {
            background-color: #f5f7fa;
            font-family: 'Segoe UI', sans-serif;
            color: #111111 !important; /* Set default font to black */
        }
        .metric-container {
            background-color: white;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 20px;
            color: #111111 !important;
        }
        .transaction-card {
            background-color: #111111;
            padding: 1rem;
            margin-bottom: 0.75rem;
            border-left: 6px solid #2c91e9;
            border-radius: 0.5rem;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            color: #000000 !important;
        }
        h1, h2, h3, h4, h5, h6, .css-10trblm, .css-1d391kg {
            color: #000000 !important;
        }
    </style>
""", unsafe_allow_html=True)

# App title
st.title("📬 Gmail Spending Tracker")
st.caption("Tracks today's spending based on your debit messages in Gmail.")

# Session state init
if "total" not in st.session_state:
    st.session_state.total = 0.0
    st.session_state.transactions = []
    st.session_state.last_updated = "--"

# Refresh button
if st.button("🔄 Refresh Now"):
    try:
        with st.spinner("🔐 Authenticating..."):
            creds = authenticate_gmail()
            service = build('gmail', 'v1', credentials=creds)

        with st.spinner("📬 Reading emails..."):
            messages = get_today_emails(service)
            total, transactions = extract_debit_amounts(service, messages)

        st.session_state.total = total
        st.session_state.transactions = transactions
        st.session_state.last_updated = time.strftime("%H:%M:%S")
        st.success("✅ Refreshed successfully!")

    except Exception as e:
        st.error(f"❌ Error: {e}")

# Metric display
st.markdown('<div class="metric-container">', unsafe_allow_html=True)
st.subheader("💰 Total Spent Today")
st.metric(label="", value=f"₹ {st.session_state.total:.2f}")
st.caption(f"Last updated at {st.session_state.last_updated}")
st.markdown('</div>', unsafe_allow_html=True)

# Transactions
st.subheader("🧾 Today's Transactions")
if st.session_state.transactions:
    for amt, desc in st.session_state.transactions:
        st.markdown(f"""
            <div class="transaction-card">
                <b>₹{amt:.2f}</b><br>
                <small>{desc}...</small>
            </div>
        """, unsafe_allow_html=True)
else:
    st.info("🎉 No spending found today!")
