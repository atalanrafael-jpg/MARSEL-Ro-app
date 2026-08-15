"""Read-only Gmail OAuth 2.0 integration.

Security model:
- OAuth client credentials come from environment variables.
- No Gmail password or token is stored in source control.
- OAuth state and the resulting credentials are held in process memory only.
- Production deployment should replace the in-memory credential store with an
  encrypted server-side store before enabling multi-worker or multi-instance use.
"""

from __future__ import annotations

import json
import os
import secrets
from dataclasses import dataclass
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

GMAIL_READONLY_SCOPE = "https://www.googleapis.com/auth/gmail.readonly"
ACCOUNT_EMAIL = "atalanrafael@gmail.com"


@dataclass
class PendingOAuth:
    state: str
    redirect_uri: str


class GmailOAuthService:
    def __init__(self) -> None:
        self._pending: dict[str, PendingOAuth] = {}
        self._credentials: Credentials | None = None

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
        self._pending[returned_state] = PendingOAuth(
            state=returned_state,
            redirect_uri=redirect_uri,
        )
        return url

    def handle_callback(self, code: str, state: str) -> dict[str, Any]:
        pending = self._pending.pop(state, None)
        if pending is None:
            raise ValueError("Invalid or expired OAuth state")

        flow = Flow.from_client_config(
            self._client_config(),
            scopes=[GMAIL_READONLY_SCOPE],
            state=state,
            redirect_uri=pending.redirect_uri,
        )
        flow.fetch_token(code=code)
        credentials = flow.credentials
        self._credentials = credentials

        profile = self._gmail_service().users().getProfile(userId="me").execute()
        email = profile.get("emailAddress")
        if email != ACCOUNT_EMAIL:
            self._credentials = None
            raise PermissionError("Authorized Google account does not match configured Gmail account")

        return {
            "status": "connected",
            "email": email,
            "scope": GMAIL_READONLY_SCOPE,
            "messages_total": profile.get("messagesTotal"),
            "threads_total": profile.get("threadsTotal"),
        }

    def status(self) -> dict[str, Any]:
        if self._credentials is None:
            return {"status": "unauthorized", "email": ACCOUNT_EMAIL}
        if self._credentials.expired and self._credentials.refresh_token:
            try:
                self._credentials.refresh(Request())
            except Exception:
                self._credentials = None
                return {"status": "token_expired", "email": ACCOUNT_EMAIL}
        return {"status": "connected", "email": ACCOUNT_EMAIL, "scope": GMAIL_READONLY_SCOPE}

    def list_messages(self, max_results: int = 10) -> list[dict[str, Any]]:
        if self._credentials is None:
            raise PermissionError("Gmail is not connected")
        service = self._gmail_service()
        response = (
            service.users()
            .messages()
            .list(userId="me", maxResults=max_results)
            .execute()
        )
        return response.get("messages", [])

    def disconnect(self) -> None:
        self._credentials = None

    def _gmail_service(self):
        if self._credentials is None:
            raise PermissionError("Gmail is not connected")
        return build("gmail", "v1", credentials=self._credentials, cache_discovery=False)


# One process-local service instance. Do not use this storage model for a
# multi-worker production deployment; use an encrypted persistent token store.
gmail_oauth = GmailOAuthService()
