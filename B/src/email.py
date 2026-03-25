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

def send_welcome_email(to_email: str, first_name: str, temp_password: str) -> None:
    subject = "Bienvenido a SAIP - Tu cuenta ha sido creada"

    html_body = f"""
    <p>Hola <strong>{first_name}</strong>,</p>
    <p>Tu cuenta en SAIP ha sido creada. Usa las siguientes credenciales para iniciar sesión:</p>
    <p><strong>Correo:</strong> {to_email}</p>
    <p><strong>Contraseña temporal:</strong> <code>{temp_password}</code></p>
    <p style="color:#c0392b;">Por seguridad, cambia tu contraseña después de iniciar sesión por primera vez.</p>
    <p>Ingresa en: <a href="http://localhost:5173/login">SAIP</a></p>
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