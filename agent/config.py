import os

def get_gemini_api_key():
    # Try each secret individually — never use 'in' operator on st.secrets
    try:
        import streamlit as st
        try:
            return st.secrets["GEMINI_API_KEY"]
        except Exception:
            pass
        try:
            return st.secrets["gemini_api_key"]
        except Exception:
            pass
        try:
            return st.secrets["GOOGLE_API_KEY"]
        except Exception:
            pass
    except Exception:
        pass
    return os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

def get_email_credentials():
    try:
        import streamlit as st
        user, pw = None, None
        try:
            user = st.secrets["GMAIL_USER"]
        except Exception:
            pass
        try:
            pw = st.secrets["GMAIL_APP_PASSWORD"]
        except Exception:
            pass
        if user and pw:
            return user, pw
    except Exception:
        pass
    return os.getenv("GMAIL_USER"), os.getenv("GMAIL_APP_PASSWORD")