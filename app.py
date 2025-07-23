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
