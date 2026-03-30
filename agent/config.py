import os
import streamlit as st

def get_gemini_api_key():
    """Get Gemini API key from st.secrets (cloud) or .env (local)."""
    try:
        return st.secrets["GEMINI_API_KEY"]
    except Exception:
        return os.getenv("GEMINI_API_KEY")

def get_email_credentials():
    """Get email credentials from st.secrets (cloud) or .env (local)."""
    try:
        return st.secrets["GMAIL_USER"], st.secrets["GMAIL_APP_PASSWORD"]
    except Exception:
        return os.getenv("GMAIL_USER"), os.getenv("GMAIL_APP_PASSWORD")