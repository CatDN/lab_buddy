# 21/03/2026

import smtplib
import cv2
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from dotenv import load_dotenv
import os

load_dotenv()

GMAIL_USER     = os.getenv("GMAIL_USER")
GMAIL_APP_PASS = os.getenv("GMAIL_APP_PASS")
ALERT_TO       = os.getenv("ALERT_TO")

def send_alert_email(reason="No reason provided", frame=None):
    msg = MIMEMultipart()
    msg['Subject'] = "Buddy Alert — Safety Check Failed"
    msg['From']    = GMAIL_USER
    msg['To']      = ALERT_TO

    # email body
    body = MIMEText(
        f"SAFETY ALERT\n\nReason: {reason}\n\nPlease check on them immediately."
    )
    msg.attach(body)

    # attach frame if provided
    if frame is not None:
        _, buffer = cv2.imencode('.jpg', frame)
        img_bytes = buffer.tobytes()
        image = MIMEImage(img_bytes, name="alert_frame.jpg")
        image.add_header('Content-Disposition', 'attachment', filename='alert_frame.jpg')
        msg.attach(image)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(GMAIL_USER, GMAIL_APP_PASS)
        server.send_message(msg)
        print("Alert email sent.")

if __name__ == "__main__":
    send_alert_email("Test alert from buddy system")