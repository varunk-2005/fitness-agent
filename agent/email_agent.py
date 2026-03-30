import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
load_dotenv()

class EmailAgent:
    def __init__(self, db_client): 
        self.db_client = db_client
        self.username = None
        # Credentials fetched lazily — not at import/init time

    @property
    def _credentials(self):
        if not hasattr(self, "_sender_email"):
            from agent.config import get_email_credentials
            self._sender_email, self._sender_password = get_email_credentials()
        return self._sender_email, self._sender_password

    def send(self, to_email, subject, body):
        sender_email, sender_password = self._credentials
        if not sender_email or not sender_password:
            return False, "Missing credentials! Please add GMAIL_USER and GMAIL_APP_PASSWORD to Streamlit Secrets."

        try:
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain', 'utf-8'))

            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to_email, msg.as_string())
            server.quit()

            return True, "Email sent successfully!"

        except smtplib.SMTPAuthenticationError:
            return False, "Google blocked the login. Make sure you are using a 16-letter App Password, not your normal Gmail password."
        except Exception as e:
            return False, f"Server error: {str(e)}"