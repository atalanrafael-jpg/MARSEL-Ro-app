import pytest

from app.gmail_oauth import ACCOUNT_EMAIL, GMAIL_READONLY_SCOPE, GmailOAuthService


def test_gmail_constants_are_read_only():
    assert ACCOUNT_EMAIL == "atalanrafael@gmail.com"
    assert GMAIL_READONLY_SCOPE.endswith("gmail.readonly")


def test_status_starts_unauthorized(monkeypatch):
    monkeypatch.delenv("GMAIL_CLIENT_ID", raising=False)
    monkeypatch.delenv("GMAIL_CLIENT_SECRET", raising=False)
    service = GmailOAuthService()
    assert service.status() == {"status": "unauthorized", "email": ACCOUNT_EMAIL}


def test_authorization_requires_client_configuration(monkeypatch):
    monkeypatch.delenv("GMAIL_CLIENT_ID", raising=False)
    monkeypatch.delenv("GMAIL_CLIENT_SECRET", raising=False)
    service = GmailOAuthService()
    with pytest.raises(RuntimeError, match="not configured"):
        service.authorization_url("https://example.com/gmail/callback")


def test_invalid_callback_state_is_rejected():
    service = GmailOAuthService()
    with pytest.raises(ValueError, match="Invalid or expired OAuth state"):
        service.handle_callback("code", "invalid-state")
