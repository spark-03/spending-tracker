
import streamlit as st
from gmail.fetch_mails import fetch_debit_emails
import pandas as pd

st.set_page_config(page_title="User Dashboard", layout="wide")

st.title("📊 Debit Summary from Gmail")
st.markdown("This dashboard fetches recent debit alerts from your Gmail and summarizes them.")

# Sidebar: Days selector
days = st.sidebar.slider("Fetch debits from the last N days", 1, 90, 30)

with st.spinner("Fetching debit emails..."):
    try:
        debits = fetch_debit_emails(days=days)
        if not debits:
            st.info("No debit transactions found in the selected period.")
        else:
            df = pd.DataFrame(debits)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values(by='date', ascending=False)

            st.success(f"✅ Found {len(df)} debit transactions")
            st.dataframe(df, use_container_width=True)

            # Optional: Total spend
            total = df['amount'].sum()
            st.metric("💸 Total Debited", f"₹{total:,.2f}")

    except Exception as e:
        st.error(f"Failed to fetch emails: {str(e)}")
