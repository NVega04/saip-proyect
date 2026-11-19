import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from html import escape

from src.core.config import settings

logger = logging.getLogger(__name__)

MAIL_HOST = settings.mail_host
MAIL_PORT = settings.mail_port
MAIL_USERNAME = settings.mail_username
MAIL_PASSWORD = settings.mail_password
MAIL_FROM = settings.mail_from


def _build_message(to_email: str, subject: str, html_body: str) -> MIMEMultipart:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = MAIL_FROM
    msg["To"] = to_email
    msg.attach(MIMEText(html_body, "html"))
    return msg


def _send_email(to_email: str, message: MIMEMultipart) -> None:
    """Envía el correo y registra fallos sin incluir credenciales."""
    try:
        with smtplib.SMTP(MAIL_HOST, MAIL_PORT) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(MAIL_USERNAME, MAIL_PASSWORD)
            server.sendmail(MAIL_FROM, to_email, message.as_string())
    except Exception:
        logger.exception("Falló el envío de correo SMTP a %s.", to_email)
        raise


def send_reset_email(to_email: str, reset_link: str) -> None:
    subject = "Recuperación de contraseña - SAIP"
    link = escape(reset_link, quote=True)

    html_body = f"""
    <p>Recibimos una solicitud para restablecer tu contraseña.</p>
    <p>Haz clic en el siguiente enlace. Expira en <strong>30 minutos</strong>.</p>
    <p><a href="{link}">Restablecer contraseña</a></p>
    <p>Si no solicitaste esto, ignora este mensaje.</p>
    """

    _send_email(to_email, _build_message(to_email, subject, html_body))


def send_welcome_email(to_email: str, first_name: str, temp_password: str) -> None:
    subject = "Bienvenido a SAIP - Tu cuenta ha sido creada"
    login_url = escape(settings.frontend_link("login"), quote=True)

    html_body = f"""
    <p>Hola <strong>{escape(first_name)}</strong>,</p>
    <p>Tu cuenta en SAIP ha sido creada. Usa las siguientes credenciales para iniciar sesión:</p>
    <p><strong>Correo:</strong> {escape(to_email)}</p>
    <p><strong>Contraseña temporal:</strong> <code>{escape(temp_password)}</code></p>
    <p style="color:#c0392b;">Por seguridad, cambia tu contraseña después de iniciar sesión por primera vez.</p>
    <p>Ingresa en: <a href="{login_url}">SAIP</a></p>
    """

    _send_email(to_email, _build_message(to_email, subject, html_body))


def send_deactivation_email(to_email: str, first_name: str) -> None:
    subject = "Tu cuenta en SAIP ha sido desactivada"

    html_body = f"""
    <p>Hola <strong>{escape(first_name)}</strong>,</p>
    <p>Te informamos que tu cuenta en <strong>SAIP</strong> ha sido <strong>desactivada</strong>.</p>
    <p>Si crees que esto es un error o necesitas más información, comunícate con el administrador del sistema.</p>
    <p>— Equipo SAIP</p>
    """

    _send_email(to_email, _build_message(to_email, subject, html_body))
