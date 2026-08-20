from concurrent.futures import ThreadPoolExecutor
import stat

import pytest
from cryptography.fernet import Fernet

import app.gmail_oauth as gmail_oauth_module
from app.gmail_oauth import (
    ACCOUNT_EMAIL,
    GMAIL_READONLY_SCOPE,
    STATE_TTL_SECONDS,
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


def test_state_is_single_use_under_concurrency(tmp_path):
    store = GmailTokenStore(str(tmp_path / "oauth.db"))
    store.save_state("concurrent-state", "https://example.com/gmail/callback")

    def consume() -> str | None:
        return store.consume_state("concurrent-state")

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(lambda _: consume(), range(2)))

    assert sorted(result is not None for result in results) == [False, True]


def test_expired_state_is_rejected_and_deleted(tmp_path, monkeypatch):
    store = GmailTokenStore(str(tmp_path / "oauth.db"))
    now = 1_000_000
    monkeypatch.setattr(gmail_oauth_module.time, "time", lambda: now)
    store.save_state("state-expired", "https://example.com/gmail/callback")

    monkeypatch.setattr(
        gmail_oauth_module.time,
        "time",
        lambda: now + STATE_TTL_SECONDS + 1,
    )
    assert store.consume_state("state-expired") is None
    assert store.consume_state("state-expired") is None


def test_storage_directory_and_database_are_owner_only(tmp_path):
    database = tmp_path / "secure" / "oauth.db"
    GmailTokenStore(str(database))

    assert stat.S_IMODE(database.parent.stat().st_mode) == 0o700
    assert stat.S_IMODE(database.stat().st_mode) == 0o600


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
