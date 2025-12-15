import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def test_send_email():
    sender_email = "yrina.lishuk2006@gmail.com"
    sender_password = "qgvv qjmd ovqa egre" 
    
    receiver_email = "tamanegichu@tuta.io"
    
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = "Тестовий лист Python"
    
    body = "Привіт! Якщо ти це читаєш, значить App Password працює вірно! 🚀"
    msg.attach(MIMEText(body, 'plain'))

    try:
        print("Connecting to Gmail...")
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  
        
        print(" Logging in...")
        server.login(sender_email, sender_password)
        
        print(" Sending a letter...")
        text = msg.as_string()
        server.sendmail(sender_email, receiver_email, text)
        
        server.quit()
        print(f"SUCCESS! Letter sent to {receiver_email}")
        
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_send_email()