import streamlit as st
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import json

# Constants
SCOPES = [
    "openid",
    "email",
    "profile",
    "https://www.googleapis.com/auth/gmail.readonly"
]

def login():
    # Initialize session state
    if "credentials" not in st.session_state:
        st.session_state.credentials = None

    # If user already logged in
    if st.session_state.credentials:
        creds = Credentials.from_authorized_user_info(st.session_state.credentials, SCOPES)
        service = build("oauth2", "v2", credentials=creds)
        user_info = service.userinfo().get().execute()
        return user_info.get("email")

    # Handle redirect URI
    redirect_uri = st.secrets["google"]["redirect_uri"]

    # First-time auth: generate URL
    if "auth_url" not in st.session_state:
        # Build the secrets dictionary from st.secrets
        client_config = {
            "web": {
                "client_id": st.secrets["google"]["client_id"],
                "client_secret": st.secrets["google"]["client_secret"],
                "redirect_uris": [redirect_uri],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": st.secrets["google"]["token_uri"]
            }
        }

        flow = Flow.from_client_config(
            client_config,
            scopes=SCOPES,
            redirect_uri=redirect_uri,
        )
        auth_url, _ = flow.authorization_url(prompt="consent")
        st.session_state.flow = flow
        st.session_state.auth_url = auth_url

        st.info("Please sign in with your Google Account:")
        st.markdown(f"[Click here to login]({auth_url})")
        return None

    # ✅ FIX: Use the correct method to get query params
    query_params = st.query_params()
    if "code" in query_params:
        code = query_params["code"][0]
        flow = st.session_state.flow
        flow.fetch_token(code=code)
        creds = flow.credentials

        # Store credentials (excluding secret)
        st.session_state.credentials = {
            "token": creds.token,
            "refresh_token": creds.refresh_token,
            "token_uri": creds.token_uri,
            "client_id": creds.client_id,
            "scopes": creds.scopes,
        }

        service = build("oauth2", "v2", credentials=creds)
        user_info = service.userinfo().get().execute()
        return user_info.get("email")

    return None
