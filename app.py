import streamlit as st
from email_reader import authenticate_gmail, get_today_emails, extract_debit_amounts
import time

# Save Gmail API credentials from Streamlit secrets
with open("credentials.json", "w") as f:
    f.write(st.secrets["credentials"])

st.set_page_config(
    page_title="Spending Tracker",
    layout="wide",
    page_icon="💸",
)

# Custom CSS styling
st.markdown("""
<style>
.big-font {
    font-size: 30px !important;
    font-weight: bold;
}
.transaction-card {
    background-color: #f5f5f5;
    padding: 12px;
    border-radius: 10px;
    margin-bottom: 8px;
    font-size: 16px;
}
.refresh-btn {
    display: inline-block;
    padding: 8px 20px;
    font-weight: bold;
    background-color: #4CAF50;
    color: white;
    border-radius: 6px;
    text-decoration: none;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>📬 Spending Tracker</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>Tracks your Gmail for today's debit transactions</p>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    if st.button("🔄 Refresh Now"):
        creds = authenticate_gmail()
        service = creds and authenticate_gmail()
        messages = get_today_emails(service)
        total, transactions = extract_debit_amounts(service, messages)
        st.session_state['total'] = total
        st.session_state['transactions'] = transactions
        st.session_state['last_updated'] = time.strftime("%I:%M %p")

with col2:
    st.markdown(f"<div style='text-align: right; font-size: 14px; color: gray;'>🕒 Last updated: {st.session_state.get('last_updated', '--')}</div>", unsafe_allow_html=True)

if 'total' not in st.session_state:
    st.session_state['total'] = 0.0
    st.session_state['transactions'] = []
    st.session_state['last_updated'] = "--"

# Display total spent today
st.markdown("<div class='big-font'>💰 Total Spent Today: ₹ {:.2f}</div>".format(st.session_state['total']), unsafe_allow_html=True)
st.markdown("---")

# Transactions
st.markdown("### 📋 Transactions")
if st.session_state['transactions']:
    for amt, detail in st.session_state['transactions']:
        st.markdown(f"<div class='transaction-card'>₹{amt:.2f} — {detail}</div>", unsafe_allow_html=True)
else:
    st.info("No transactions found for today 🙌")

st.markdown("<br><hr><p style='text-align: center; font-size: 12px;'>Made with 💚 using Gmail & Streamlit</p>", unsafe_allow_html=True)
