"""Regresiones del rate limit global de la Fase 3."""

from types import SimpleNamespace

import pytest
from fastapi import Request

from src.core.config import settings
from src.core.rate_limit import client_ip, limiter


@pytest.mark.unit
def test_default_limit_is_configured():
    assert settings.rate_limit_default == "100/minute"
    assert limiter._default_limits  # noqa: SLF001 - comprobación intencional


@pytest.mark.unit
def test_trusted_proxy_header_is_only_used_for_known_hosts(monkeypatch):
    request: Request = SimpleNamespace(  # type: ignore[assignment]
        client=SimpleNamespace(host="10.0.0.1"),
        headers={"x-forwarded-for": "1.2.3.4, 5.6.7.8"},
    )

    monkeypatch.setattr(settings, "trusted_proxy_hosts", [])
    assert client_ip(request) == "10.0.0.1"

    monkeypatch.setattr(settings, "trusted_proxy_hosts", ["10.0.0.1"])
    assert client_ip(request) == "1.2.3.4"


@pytest.mark.unit
def test_login_limit_is_enforced(client, monkeypatch):
    storage = limiter._storage  # noqa: SLF001 - se limpia el contador de la suite
    storage.reset()
    monkeypatch.setattr(limiter, "enabled", True)

    try:
        responses = [
            client.post(
                "/session/login",
                json={
                    "email": "no-existe@saip.com",
                    "password": "ClaveIncorrecta123!",
                },
            )
            for _ in range(6)
        ]

        assert [r.status_code for r in responses[:5]] == [401] * 5
        assert responses[5].status_code == 429
    finally:
        storage.reset()
