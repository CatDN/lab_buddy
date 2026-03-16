# 14/03/2026
import smtplib
from email.mime.text import MIMEText

# to access email
from dotenv import load_dotenv
import os

load_dotenv()

GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_APP_PASS = os.getenv("GMAIL_APP_PASS")
ALERT_TO = os.getenv("ALERT_TO")

def send_alert_email(reason="No reson provided"):
    msg = MIMEText(
        f"SAFETY ALERT\n\nReason: {reason}\n\nPlease check on them immediately."
    )

    msg['Subject'] = "Buddy Alert — Safety Check Failed"
    msg['From']    = GMAIL_USER
    msg['To']      = ALERT_TO

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(GMAIL_USER, GMAIL_APP_PASS)
        server.send_message(msg)
        print("Alert email sent.")

if __name__ == "__main__":
    send_alert_email("Test alert from buddy system")