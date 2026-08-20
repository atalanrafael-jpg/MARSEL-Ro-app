"""Read-only Gmail OAuth 2.0 integration with persistent encrypted storage.

Security model:
- OAuth client credentials come from environment variables.
- Refresh/access credentials are encrypted at rest with Fernet.
- OAuth state is stored server-side with a TTL and consumed atomically once.
- No Gmail password or token is stored in source control.
- The token encryption key must be supplied by the runtime secret manager.
"""

from __future__ import annotations

import hashlib
import json
import os
import secrets
import sqlite3
import time
from pathlib import Path
from typing import Any

from cryptography.fernet import Fernet, InvalidToken
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

GMAIL_READONLY_SCOPE = "https://www.googleapis.com/auth/gmail.readonly"
ACCOUNT_EMAIL = "atalanrafael@gmail.com"
DEFAULT_STORE_PATH = "~/.local/share/marsel/gmail_oauth.db"
STATE_TTL_SECONDS = 600


class GmailTokenStore:
    """SQLite-backed store safe for multiple workers on the same host."""

    def __init__(self, path: str | None = None) -> None:
        configured_path = path or os.getenv("GMAIL_TOKEN_STORE_PATH", DEFAULT_STORE_PATH)
        self.path = Path(configured_path).expanduser()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, timeout=10)
        connection.execute("PRAGMA busy_timeout = 10000")
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                "CREATE TABLE IF NOT EXISTS oauth_state ("
                "state_hash TEXT PRIMARY KEY, redirect_uri TEXT NOT NULL, created_at INTEGER NOT NULL)"
            )
            connection.execute(
                "CREATE TABLE IF NOT EXISTS gmail_credentials ("
                "account_email TEXT PRIMARY KEY, encrypted_credentials BLOB NOT NULL, updated_at INTEGER NOT NULL)"
            )

    def save_state(self, state: str, redirect_uri: str) -> None:
        state_hash = hashlib.sha256(state.encode("utf-8")).hexdigest()
        now = int(time.time())
        with self._connect() as connection:
            connection.execute("DELETE FROM oauth_state WHERE created_at < ?", (now - STATE_TTL_SECONDS,))
            connection.execute(
                "INSERT INTO oauth_state(state_hash, redirect_uri, created_at) VALUES (?, ?, ?)",
                (state_hash, redirect_uri, now),
            )

    def consume_state(self, state: str) -> str | None:
        state_hash = hashlib.sha256(state.encode("utf-8")).hexdigest()
        now = int(time.time())
        with self._connect() as connection:
            row = connection.execute(
                "SELECT redirect_uri, created_at FROM oauth_state WHERE state_hash = ?",
                (state_hash,),
            ).fetchone()
            if row is None:
                return None
            connection.execute("DELETE FROM oauth_state WHERE state_hash = ?", (state_hash,))
            if row[1] < now - STATE_TTL_SECONDS:
                return None
            return str(row[0])

    def save_credentials(self, account_email: str, encrypted_credentials: bytes) -> None:
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO gmail_credentials(account_email, encrypted_credentials, updated_at) "
                "VALUES (?, ?, ?) ON CONFLICT(account_email) DO UPDATE SET "
                "encrypted_credentials=excluded.encrypted_credentials, updated_at=excluded.updated_at",
                (account_email, encrypted_credentials, int(time.time())),
            )

    def load_credentials(self, account_email: str) -> bytes | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT encrypted_credentials FROM gmail_credentials WHERE account_email = ?",
                (account_email,),
            ).fetchone()
        return None if row is None else bytes(row[0])

    def delete_credentials(self, account_email: str) -> None:
        with self._connect() as connection:
            connection.execute("DELETE FROM gmail_credentials WHERE account_email = ?", (account_email,))


class GmailOAuthService:
    def __init__(self, store: GmailTokenStore | None = None) -> None:
        self._store = store or GmailTokenStore()

    def _fernet(self) -> Fernet:
        key = os.getenv("GMAIL_TOKEN_ENCRYPTION_KEY", "")
        if not key:
            raise RuntimeError("Gmail token encryption key is not configured")
        try:
            return Fernet(key.encode("utf-8"))
        except (ValueError, TypeError) as exc:
            raise RuntimeError("Gmail token encryption key is invalid") from exc

    def _client_config(self) -> dict[str, Any]:
        client_id = os.getenv("GMAIL_CLIENT_ID", "")
        client_secret = os.getenv("GMAIL_CLIENT_SECRET", "")
        if not client_id or not client_secret:
            raise RuntimeError("Gmail OAuth client is not configured")
        return {
            "web": {
                "client_id": client_id,
                "client_secret": client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [],
            }
        }

    def authorization_url(self, redirect_uri: str) -> str:
        state = secrets.token_urlsafe(32)
        flow = Flow.from_client_config(
            self._client_config(),
            scopes=[GMAIL_READONLY_SCOPE],
            redirect_uri=redirect_uri,
        )
        url, returned_state = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent",
            state=state,
        )
        self._store.save_state(returned_state, redirect_uri)
        return url

    def handle_callback(self, code: str, state: str) -> dict[str, Any]:
        redirect_uri = self._store.consume_state(state)
        if redirect_uri is None:
            raise ValueError("Invalid or expired OAuth state")

        flow = Flow.from_client_config(
            self._client_config(),
            scopes=[GMAIL_READONLY_SCOPE],
            state=state,
            redirect_uri=redirect_uri,
        )
        flow.fetch_token(code=code)
        credentials = flow.credentials

        profile = self._gmail_service(credentials).users().getProfile(userId="me").execute()
        email = profile.get("emailAddress")
        if email != ACCOUNT_EMAIL:
            raise PermissionError("Authorized Google account does not match configured Gmail account")

        encrypted = self._fernet().encrypt(credentials.to_json().encode("utf-8"))
        self._store.save_credentials(ACCOUNT_EMAIL, encrypted)

        return {
            "status": "connected",
            "email": email,
            "scope": GMAIL_READONLY_SCOPE,
            "messages_total": profile.get("messagesTotal"),
            "threads_total": profile.get("threadsTotal"),
        }

    def _load_credentials(self) -> Credentials | None:
        encrypted = self._store.load_credentials(ACCOUNT_EMAIL)
        if encrypted is None:
            return None
        try:
            raw = self._fernet().decrypt(encrypted).decode("utf-8")
            return Credentials.from_authorized_user_info(json.loads(raw), scopes=[GMAIL_READONLY_SCOPE])
        except (InvalidToken, ValueError, TypeError, json.JSONDecodeError) as exc:
            raise RuntimeError("Stored Gmail credentials are invalid or cannot be decrypted") from exc

    def status(self) -> dict[str, Any]:
        credentials = self._load_credentials()
        if credentials is None:
            return {"status": "unauthorized", "email": ACCOUNT_EMAIL}
        if credentials.expired and credentials.refresh_token:
            try:
                credentials.refresh(Request())
                encrypted = self._fernet().encrypt(credentials.to_json().encode("utf-8"))
                self._store.save_credentials(ACCOUNT_EMAIL, encrypted)
            except Exception:
                self._store.delete_credentials(ACCOUNT_EMAIL)
                return {"status": "token_expired", "email": ACCOUNT_EMAIL}
        return {"status": "connected", "email": ACCOUNT_EMAIL, "scope": GMAIL_READONLY_SCOPE}

    def list_messages(self, max_results: int = 10) -> list[dict[str, Any]]:
        credentials = self._load_credentials()
        if credentials is None:
            raise PermissionError("Gmail is not connected")
        if credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
            self._store.save_credentials(
                ACCOUNT_EMAIL,
                self._fernet().encrypt(credentials.to_json().encode("utf-8")),
            )
        response = (
            self._gmail_service(credentials)
            .users()
            .messages()
            .list(userId="me", maxResults=max_results)
            .execute()
        )
        return response.get("messages", [])

    def disconnect(self) -> None:
        self._store.delete_credentials(ACCOUNT_EMAIL)

    @staticmethod
    def _gmail_service(credentials: Credentials):
        return build("gmail", "v1", credentials=credentials, cache_discovery=False)


gmail_oauth = GmailOAuthService()
