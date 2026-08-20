import os

import pytest
from cryptography.fernet import Fernet

from app.gmail_oauth import (
    ACCOUNT_EMAIL,
    GMAIL_READONLY_SCOPE,
    GmailOAuthService,
    GmailTokenStore,
)


def test_gmail_constants_are_read_only():
    assert ACCOUNT_EMAIL == "atalanrafael@gmail.com"
    assert GMAIL_READONLY_SCOPE.endswith("gmail.readonly")


def test_state_is_persistent_and_single_use(tmp_path):
    store = GmailTokenStore(str(tmp_path / "oauth.db"))
    store.save_state("state-123", "https://example.com/gmail/callback")

    assert store.consume_state("state-123") == "https://example.com/gmail/callback"
    assert store.consume_state("state-123") is None


def test_credentials_are_encrypted_at_rest(tmp_path):
    store = GmailTokenStore(str(tmp_path / "oauth.db"))
    plaintext = b'{"refresh_token":"secret"}'
    encrypted = Fernet(Fernet.generate_key()).encrypt(plaintext)
    store.save_credentials(ACCOUNT_EMAIL, encrypted)

    stored = store.load_credentials(ACCOUNT_EMAIL)
    assert stored == encrypted
    assert plaintext not in stored


def test_status_requires_encryption_key(tmp_path, monkeypatch):
    monkeypatch.delenv("GMAIL_TOKEN_ENCRYPTION_KEY", raising=False)
    service = GmailOAuthService(GmailTokenStore(str(tmp_path / "oauth.db")))
    with pytest.raises(RuntimeError, match="encryption key is not configured"):
        service.status()


def test_invalid_encryption_key_is_rejected(tmp_path, monkeypatch):
    monkeypatch.setenv("GMAIL_TOKEN_ENCRYPTION_KEY", "not-a-fernet-key")
    service = GmailOAuthService(GmailTokenStore(str(tmp_path / "oauth.db")))
    with pytest.raises(RuntimeError, match="encryption key is invalid"):
        service.status()


def test_status_starts_unauthorized_with_valid_runtime_key(tmp_path, monkeypatch):
    monkeypatch.setenv("GMAIL_TOKEN_ENCRYPTION_KEY", Fernet.generate_key().decode())
    service = GmailOAuthService(GmailTokenStore(str(tmp_path / "oauth.db")))
    assert service.status() == {"status": "unauthorized", "email": ACCOUNT_EMAIL}


def test_authorization_requires_client_configuration(tmp_path, monkeypatch):
    monkeypatch.delenv("GMAIL_CLIENT_ID", raising=False)
    monkeypatch.delenv("GMAIL_CLIENT_SECRET", raising=False)
    monkeypatch.setenv("GMAIL_TOKEN_ENCRYPTION_KEY", Fernet.generate_key().decode())
    service = GmailOAuthService(GmailTokenStore(str(tmp_path / "oauth.db")))
    with pytest.raises(RuntimeError, match="not configured"):
        service.authorization_url("https://example.com/gmail/callback")


def test_invalid_callback_state_is_rejected(tmp_path, monkeypatch):
    monkeypatch.setenv("GMAIL_TOKEN_ENCRYPTION_KEY", Fernet.generate_key().decode())
    service = GmailOAuthService(GmailTokenStore(str(tmp_path / "oauth.db")))
    with pytest.raises(ValueError, match="Invalid or expired OAuth state"):
        service.handle_callback("code", "invalid-state")
