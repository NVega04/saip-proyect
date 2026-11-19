"""Tests de CORS configurable (Fase 2)."""

from src.core.config import settings

PREFLIGHT_HEADERS = {
    "Access-Control-Request-Method": "GET",
    "Access-Control-Request-Headers": "session-token",
}


def test_configured_origin_is_allowed(client):
    origin = settings.cors_origins[0]

    response = client.options("/health", headers={**PREFLIGHT_HEADERS, "Origin": origin})

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == origin
    assert "session-token" in response.headers["access-control-allow-headers"]


def test_unknown_origin_is_rejected(client):
    response = client.options(
        "/health", headers={**PREFLIGHT_HEADERS, "Origin": "http://evil.example"}
    )

    assert response.status_code == 400
    assert "access-control-allow-origin" not in response.headers


def test_origin_with_trailing_slash_is_rejected(client):
    response = client.options(
        "/health",
        headers={**PREFLIGHT_HEADERS, "Origin": f"{settings.cors_origins[0]}/"},
    )

    assert response.status_code == 400


def test_no_wildcards_or_hardcoded_origins_remain():
    assert all("*" not in origin for origin in settings.cors_origins)
    assert all(origin.startswith(("http://", "https://")) for origin in settings.cors_origins)
    assert "exp://*" not in settings.cors_origins
    assert "http://161.35.6.77:5173" not in settings.cors_origins
