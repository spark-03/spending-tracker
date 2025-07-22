import streamlit as st
import os
import json
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Path to your client_secret.json
CLIENT_SECRET_FILE = "credentials/client_secret.json"
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly", "openid", "email", "profile"]

def login():
    if "credentials" not in st.session_state:
        st.session_state.credentials = None

    if st.session_state.credentials:
        creds = Credentials.from_authorized_user_info(st.session_state.credentials, SCOPES)
        service = build("oauth2", "v2", credentials=creds)
        user_info = service.userinfo().get().execute()
        return user_info.get("email")

    # Start OAuth flow
    if "auth_url" not in st.session_state:
        flow = Flow.from_client_secrets_file(
            CLIENT_SECRET_FILE,
            scopes=SCOPES,
            redirect_uri="http://localhost:8501"
        )
        auth_url, _ = flow.authorization_url(prompt='consent')
        st.session_state.flow = flow
        st.session_state.auth_url = auth_url
        st.info("Please sign in with your Google Account:")
        st.markdown(f"[Click here to login]({auth_url})")
        return None

    # Once redirected back, extract credentials from URL params
    if "code" in st.experimental_get_query_params():
        code = st.experimental_get_query_params()["code"][0]
        flow = st.session_state.flow
        flow.fetch_token(code=code)
        creds = flow.credentials
        st.session_state.credentials = {
            "token": creds.token,
            "refresh_token": creds.refresh_token,
            "token_uri": creds.token_uri,
            "client_id": creds.client_id,
            "client_secret": creds.client_secret,
            "scopes": creds.scopes
        }
        service = build("oauth2", "v2", credentials=creds)
        user_info = service.userinfo().get().execute()
        return user_info.get("email")

    return None
