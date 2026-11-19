"""Tests de enlaces y registro de errores de correo (Fase 2)."""

import logging
from email import message_from_string
from pathlib import Path

import pytest

from src.core import email as email_module
from src.core.config import settings

BACKEND_DIR = Path(__file__).resolve().parents[1]

SENT_MESSAGES = []


def sent_body() -> str:
    message = message_from_string(SENT_MESSAGES[0])
    return message.get_payload(0).get_payload(decode=True).decode("utf-8")


class FakeSMTP:
    fail_login = False

    def __init__(self, host, port):
        self.host = host
        self.port = port

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def ehlo(self):
        pass

    def starttls(self):
        pass

    def login(self, username, password):
        if self.fail_login:
            raise RuntimeError("falló la autenticación SMTP")

    def sendmail(self, from_email, to_email, message):
        SENT_MESSAGES.append(message)


@pytest.fixture(autouse=True)
def fake_smtp(monkeypatch):
    SENT_MESSAGES.clear()
    FakeSMTP.fail_login = False
    monkeypatch.setattr(email_module.smtplib, "SMTP", FakeSMTP)


def test_no_hardcoded_frontend_links_in_email_templates():
    source = (BACKEND_DIR / "src/core/email.py").read_text()
    assert "http://localhost:5173" not in source
    assert "frontend_link" in source


def test_welcome_email_link_comes_from_settings(monkeypatch):
    monkeypatch.setattr(settings, "frontend_url", "https://saip.lat")

    email_module.send_welcome_email("ana@saip.com", "Ana", "Pass1234!xyz")

    body = sent_body()
    assert "https://saip.lat/login" in body
    assert "localhost:5173" not in body


def test_reset_email_uses_generated_link():
    link = "https://saip.lat/reset-password?token=abc123"

    email_module.send_reset_email("ana@saip.com", link)

    body = sent_body()
    assert link in body


def test_smtp_failure_is_logged_without_password(caplog, monkeypatch):
    FakeSMTP.fail_login = True
    secret = "super-contrasena-smtp"
    monkeypatch.setattr(email_module, "MAIL_PASSWORD", secret)

    with caplog.at_level(logging.ERROR):
        with pytest.raises(RuntimeError):
            email_module.send_welcome_email("ana@saip.com", "Ana", "Pass1234!xyz")

    assert "Falló el envío de correo SMTP" in caplog.text
    assert secret not in caplog.text
