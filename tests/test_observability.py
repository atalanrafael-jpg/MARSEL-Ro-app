import json
import logging

from fastapi.testclient import TestClient

from app.main import app


def test_health_emits_correlation_telemetry(caplog):
    caplog.set_level(logging.INFO, logger="marsel.observability")
    with TestClient(app) as client:
        response = client.get(
            "/health",
            headers={"X-Request-ID": "req-test-1", "X-Correlation-ID": "corr-test-1"},
        )

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "req-test-1"
    assert response.headers["X-Correlation-ID"] == "corr-test-1"

    event = next(json.loads(record.message) for record in caplog.records if record.name == "marsel.observability")
    assert event["request_id"] == "req-test-1"
    assert event["correlation_id"] == "corr-test-1"
    assert event["endpoint"] == "/health"
    assert event["http_status"] == 200
    assert "authorization" not in event
    assert "cookie" not in event


def test_observability_does_not_log_internal_api_key(caplog, monkeypatch):
    from app.config import settings

    monkeypatch.setattr(settings, "marsel_internal_api_key", "super-secret-test-key")
    caplog.set_level(logging.INFO, logger="marsel.observability")
    with TestClient(app) as client:
        response = client.get(
            "/roapp/orders",
            headers={
                "X-MARSEL-API-Key": "super-secret-test-key",
                "X-Request-ID": "req-secret-test",
            },
        )

    assert response.status_code in {200, 502, 503}
    assert "super-secret-test-key" not in caplog.text
