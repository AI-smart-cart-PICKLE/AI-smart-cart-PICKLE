# app/utils/email.py

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from os import getenv

SMTP_HOST = getenv("SMTP_HOST")
SMTP_PORT = int(getenv("SMTP_PORT"))
SMTP_USER = getenv("SMTP_USER")
SMTP_PASSWORD = getenv("SMTP_PASSWORD")


def send_reset_password_email(to_email: str, reset_link: str):
    msg = MIMEMultipart()
    msg["From"] = SMTP_USER
    msg["To"] = to_email
    msg["Subject"] = "[SmartCart] 비밀번호 재설정 안내"

    body = f"""
안녕하세요.

아래 링크를 클릭하여 비밀번호를 재설정해주세요.

{reset_link}

본 링크는 일정 시간 후 만료됩니다.
"""
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)
