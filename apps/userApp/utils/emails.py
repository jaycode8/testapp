
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
import os

load_dotenv()
sender = os.getenv("sender")
password = os.getenv("password")


def transporter(receiver, otp):
    service = smtplib.SMTP("smtp.gmail.com", 587)
    service.starttls()
    service.login(sender, password)
    message = EmailMessage()
    message["Subject"] = "Account verification"
    message["From"] = sender
    message["To"] = receiver
    message.set_content(f"Verification code is {otp}")
    try:
        service.send_message(message)
    except Exception as e:
        return False
    service.quit()
    return True
