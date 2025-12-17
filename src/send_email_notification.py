import os

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

def send_email_notification(to_email: str, subject: str, message: str):
    if os.getenv("ENV") == "test":
        return
    
    sender_email = os.getenv("EMAIL_SENDER")
    sender_password = os.getenv("EMAIL_PASSWORD")

    if not sender_email or not sender_password:
        raise RuntimeError("Email credentials not set")
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain')) 

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()
        print(f"Letter successfully sent to {to_email}")
    except Exception as e:
        print(f"Error sending mail: {e}")
