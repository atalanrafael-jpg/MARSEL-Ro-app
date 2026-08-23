import pytest

from app.gmail_oauth import GMAIL_READONLY_SCOPE, GmailOAuthService


def test_gmail_oauth_uses_readonly_scope(monkeypatch):
    monkeypatch.setenv("GMAIL_CLIENT_ID", "client-id")
    monkeypatch.setenv("GMAIL_CLIENT_SECRET", "client-secret")
    service = GmailOAuthService()

    config = service._client_config()

    assert config["web"]["client_id"] == "client-id"
    assert config["web"]["client_secret"] == "client-secret"
    assert GMAIL_READONLY_SCOPE == "https://www.googleapis.com/auth/gmail.readonly"


def test_gmail_oauth_requires_client_credentials(monkeypatch):
    monkeypatch.delenv("GMAIL_CLIENT_ID", raising=False)
    monkeypatch.delenv("GMAIL_CLIENT_SECRET", raising=False)
    service = GmailOAuthService()

    with pytest.raises(RuntimeError, match="not configured"):
        service._client_config()


def test_gmail_oauth_rejects_unknown_state():
    service = GmailOAuthService()

    with pytest.raises(ValueError, match="Invalid or expired OAuth state"):
        service.handle_callback("code", "unknown-state")


def test_gmail_oauth_limits_message_count(monkeypatch):
    service = GmailOAuthService()
    service._credentials = object()  # bypass network; validation happens first

    for value in (0, 101):
        with pytest.raises(ValueError, match="от 1 до 100"):
            service.list_messages(value)
