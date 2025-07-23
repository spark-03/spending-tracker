import streamlit as st
from streamlit_extras.badges import badge
from streamlit_extras.stylable_container import stylable_container
from streamlit_extras.let_it_rain import rain
from streamlit_extras.metric_cards import style_metric_cards

from auth.login import login

# --- Auth ---
user_email = login()
if not user_email:
    st.stop()

# --- Page config ---
st.set_page_config(page_title="Today's Spend", page_icon="💸", layout="centered")
st.success(f"Welcome, {user_email} 👋")

# --- Imports ---
try:
    from email_reader import get_today_spending
except Exception as e:
    st.error("❌ Failed to import `email_reader.py`")
    st.exception(e)
    st.stop()

# --- UI Header ---
st.markdown("""
    <h1 style='text-align: center; color: #4CAF50; font-size: 28px'>
        💳 Today's Debit Summary
    </h1>
""", unsafe_allow_html=True)

# --- Optional Animation ---
rain(emoji="💸", font_size=28, falling_speed=5, animation_length="short")

# --- Fetch Data ---
with st.spinner("🔍 Fetching today's debit messages..."):
    data = get_today_spending()

# --- Display Data ---
if not data:
    st.warning("🚫 No debit transactions found today.")
else:
    total = sum(d['amount'] for d in data)

    st.markdown("### 💰 Summary")
    st.metric(label="Total Debited Today", value=f"₹{total:,.2f}")
    style_metric_cards(background_color="111111", border_color="#4CAF50", border_left_color="#4CAF50", box_shadow=True)

    st.markdown("---")
    st.markdown("### 📋 Transaction Details")

    for txn in data:
        with stylable_container(
            key=f"txn_{txn['time']}",
            css_styles="""
                {
                    background-color: #111111;
                    padding: 16px;
                    border-radius: 12px;
                    border: 1px solid #e0e0e0;
                    margin-bottom: 10px;
                    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
                }
            """
        ):
            st.markdown(f"**🕒 {txn['time']}**  &nbsp;&nbsp; —  &nbsp;&nbsp; `₹{txn['amount']}`")
            st.markdown(f"**🔸 Purpose:** {txn['purpose']}")
            st.caption(f"📩 {txn['subject']}")

# --- Footer ---
st.markdown("---")
st.markdown("<div style='text-align:center; color: black;'>Built with ❤️ using Streamlit</div>", unsafe_allow_html=True)
