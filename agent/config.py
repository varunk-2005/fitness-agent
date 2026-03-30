import os

def get_gemini_api_key():
    # Try Streamlit secrets first (handles both flat and nested TOML)
    try:
        import streamlit as st
        secrets = st.secrets
        # Try common key names in order
        for key in ("GEMINI_API_KEY", "gemini_api_key", "GOOGLE_API_KEY", "google_api_key"):
            if key in secrets:
                return secrets[key]
        # Try nested: [gemini] section with api_key
        if "gemini" in secrets and "api_key" in secrets["gemini"]:
            return secrets["gemini"]["api_key"]
        if "google" in secrets and "api_key" in secrets["google"]:
            return secrets["google"]["api_key"]
    except Exception:
        pass

    # Fallback to environment variable
    return os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")


def get_email_credentials():
    try:
        import streamlit as st
        secrets = st.secrets
        user = None
        password = None

        for key in ("GMAIL_USER", "gmail_user"):
            if key in secrets:
                user = secrets[key]
                break
        for key in ("GMAIL_APP_PASSWORD", "gmail_app_password"):
            if key in secrets:
                password = secrets[key]
                break

        if "gmail" in secrets:
            user = user or secrets["gmail"].get("user")
            password = password or secrets["gmail"].get("app_password")

        if user and password:
            return user, password
    except Exception:
        pass

    return os.getenv("GMAIL_USER"), os.getenv("GMAIL_APP_PASSWORD")