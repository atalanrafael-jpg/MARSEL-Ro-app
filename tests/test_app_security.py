from fastapi.testclient import TestClient

from app.config import settings
from app.main import app


def test_roapp_orders_requires_internal_auth(monkeypatch):
    monkeypatch.setattr(settings, "marsel_internal_api_key", "test-internal-key")
    with TestClient(app) as client:
        response = client.get("/roapp/orders")
    assert response.status_code == 401


def test_roapp_orders_rejects_wrong_internal_auth(monkeypatch):
    monkeypatch.setattr(settings, "marsel_internal_api_key", "test-internal-key")
    with TestClient(app) as client:
        response = client.get(
            "/roapp/orders",
            headers={"X-MARSEL-API-Key": "wrong-key"},
        )
    assert response.status_code == 401


def test_roapp_orders_does_not_call_upstream_on_auth_failure(monkeypatch):
    monkeypatch.setattr(settings, "marsel_internal_api_key", "test-internal-key")

    def fail_if_called(*args, **kwargs):
        raise AssertionError("RO App upstream must not be contacted before caller auth")

    monkeypatch.setattr("app.main.RoAppClient.get_orders", fail_if_called)
    with TestClient(app) as client:
        response = client.get("/roapp/orders")
    assert response.status_code == 401


def test_ready_does_not_disclose_secret_presence(monkeypatch):
    monkeypatch.setattr(settings, "roapp_api_key", "real-looking-secret")
    monkeypatch.setattr(settings, "marsel_internal_api_key", "another-secret")
    with TestClient(app) as client:
        payload = client.get("/ready").json()
    assert "api_key_configured" not in payload
    assert "real-looking-secret" not in str(payload)
    assert "another-secret" not in str(payload)
