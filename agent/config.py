import os

def get_gemini_api_key():
    try:
        import streamlit as st
        return st.secrets["GEMINI_API_KEY"]
    except Exception:
        return os.getenv("GEMINI_API_KEY")

def get_email_credentials():
    try:
        import streamlit as st
        return st.secrets["GMAIL_USER"], st.secrets["GMAIL_APP_PASSWORD"]
    except Exception:
        return os.getenv("GMAIL_USER"), os.getenv("GMAIL_APP_PASSWORD")