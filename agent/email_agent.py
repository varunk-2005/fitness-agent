import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import streamlit as st
from agent.config import get_email_credentials
load_dotenv()

class EmailAgent:
    def __init__(self, db_client): 
        self.db_client = db_client
        self.username = None       
        self.sender_email, self.sender_password = get_email_credentials()

    def send(self, to_email, subject, body):
        """Dispatches the email via Google's SMTP server."""
        if not self.sender_email or not self.sender_password:
            return False, "Missing credentials! Please add EMAIL_ADDRESS and EMAIL_PASSWORD to your .env or Streamlit Secrets."

        try:
    
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = to_email
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'plain', 'utf-8'))

            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            
            server.login(self.sender_email, self.sender_password)
            server.sendmail(self.sender_email, to_email, msg.as_string())
            server.quit()

            return True, "Email sent successfully!"
            
        except smtplib.SMTPAuthenticationError:
            return False, "Google blocked the login. Make sure you are using a 16-letter App Password, not your normal Gmail password."
        except Exception as e:
            return False, f"Server error: {str(e)}"