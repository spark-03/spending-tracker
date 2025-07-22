import streamlit as st
from streamlit_extras.badges import badge
from streamlit_extras.stylable_container import stylable_container
from streamlit_extras.let_it_rain import rain
from streamlit_extras.metric_cards import style_metric_cards

from auth.login import login

user_email = login()
if not user_email:
    st.stop()

st.success(f"Welcome, {user_email} 👋")
# Show your dashboard or analytics after this
if not login():
    st.stop()  # Stops execution until logged in
try:
    from email_reader import get_today_spending
except Exception as e:
    st.error("❌ Failed to import `email_reader.py`")
    st.exception(e)

# Set page config
st.set_page_config(page_title="Today's Spend", page_icon="💸", layout="centered")

# Title with emoji and style
st.markdown("""
    <h1 style='text-align: center; color: #4CAF50; font_size=24'>
        💳 Today's Debit Summary
    </h1>
""", unsafe_allow_html=True)

# Optional animation (confetti when app loads)
rain(emoji="💸", font_size=28, falling_speed=5, animation_length="short")

with st.spinner("🔍 Fetching today's debit messages..."):
    data = get_today_spending()

if not data:
    st.warning("🚫 No debit transactions found today.")
else:
    total = sum(d['amount'] for d in data)

    # Stylish metric
    st.markdown("### 💰 Summary")
    st.metric(label="Total Debited Today", value=f"₹{total:,.2f}", delta=None)
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

# Footer or credit
st.markdown("---")
st.markdown("<div style='text-align:center; color: black;'>Built with ❤️ using Streamlit</div>", unsafe_allow_html=True)
