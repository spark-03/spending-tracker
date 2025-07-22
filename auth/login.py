# auth/login.py

import streamlit as st
import os
import streamlit_authenticator as stauth
from dotenv import load_dotenv

# Load environment variables (optional)
load_dotenv()

# Replace with your own hashed password(s)
hashed_passwords = stauth.Hasher(["your_plain_password"]).generate()

# Example: one user only
authenticator = stauth.Authenticate(
    names=["Demo User"],
    usernames=["demo_user"],
    passwords=hashed_passwords,
    cookie_name="spending_tracker_login",
    key="auth",
    cookie_expiry_days=30
)

def login():
    name, auth_status, username = authenticator.login("Login", "main")

    if auth_status is False:
        st.error("Username/password is incorrect")
    elif auth_status is None:
        st.warning("Please enter your username and password")
    elif auth_status:
        st.success(f"Welcome, {name} 👋")
        return True  # Logged in successfully
    return False  # Not logged in yet
