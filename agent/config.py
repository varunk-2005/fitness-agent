import os

def get_gemini_api_key():
    # Try each secret individually — never use 'in' operator on st.secrets
    try:
        import streamlit as st
        key = st.secrets.get("GEMINI_API_KEY") or st.secrets.get("gemini_api_key") or st.secrets.get("GOOGLE_API_KEY")
        if key:
            return str(key).strip()
    except Exception:
        pass
    
    env_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if env_key:
        return str(env_key).strip()
        
    raise ValueError("GEMINI_API_KEY is missing! Please set it in your Streamlit Cloud Secrets dashboard.")

def get_email_credentials():
    try:
        import streamlit as st
        user = st.secrets.get("GMAIL_USER")
        pw = st.secrets.get("GMAIL_APP_PASSWORD")
        if user and pw:
            return user, pw
    except Exception:
        pass
    return os.getenv("GMAIL_USER"), os.getenv("GMAIL_APP_PASSWORD")