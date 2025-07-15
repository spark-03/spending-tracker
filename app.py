import streamlit as st
try:
    from email_reader import get_today_spending
except Exception as e:
    st.error("Failed to import email_reader.py")
    st.exception(e)

from email_reader import get_today_spending

st.set_page_config(page_title="Today's Spend", page_icon="💸")
st.title("💸 Today's Debit Summary")

with st.spinner("Fetching today's debit messages..."):
    data = get_today_spending()

if not data:
    st.warning("No debit transactions found today.")
else:
    total = sum(d['amount'] for d in data)
    st.metric("💰 Total Debited Today", f"₹{total:,.2f}")
    st.divider()
    for txn in data:
        st.write(f"🕒 **{txn['time']}** — ₹{txn['amount']} → {txn['purpose']}")
        st.caption(f"📩 {txn['subject']}")
        st.markdown("---")
