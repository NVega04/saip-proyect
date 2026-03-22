import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

MAIL_HOST     = os.getenv("MAIL_HOST")
MAIL_PORT     = int(os.getenv("MAIL_PORT", 587))
MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_FROM     = os.getenv("MAIL_FROM")

def send_reset_email(to_email: str, reset_link: str) -> None:
    subject = "Recuperación de contraseña - SAIP"

    html_body = f"""
    <p>Recibimos una solicitud para restablecer tu contraseña.</p>
    <p>Haz clic en el siguiente enlace. Expira en <strong>30 minutos</strong>.</p>
    <p><a href="{reset_link}">Restablecer contraseña</a></p>
    <p>Si no solicitaste esto, ignora este mensaje.</p>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = MAIL_FROM
    msg["To"]      = to_email
    msg.attach(MIMEText(html_body, "html"))

    server = smtplib.SMTP(MAIL_HOST, MAIL_PORT)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(MAIL_USERNAME, MAIL_PASSWORD)
    server.sendmail(MAIL_FROM, to_email, msg.as_string())
    server.quit()