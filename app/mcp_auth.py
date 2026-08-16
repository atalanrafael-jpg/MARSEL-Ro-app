from __future__ import annotations

import asyncio
import logging
from typing import Any

import jwt
from jwt import PyJWKClient
from mcp.server.auth.provider import AccessToken, TokenVerifier

logger = logging.getLogger(__name__)


class JWTTokenVerifier(TokenVerifier):
    """Verify signed OAuth access tokens using JWKS, issuer and audience checks."""

    def __init__(
        self,
        *,
        jwks_url: str,
        issuer: str,
        audience: str,
        algorithms: tuple[str, ...] = ("RS256",),
    ) -> None:
        if not jwks_url.startswith("https://"):
            raise ValueError("MCP_AUTH_JWKS_URL must use HTTPS")
        if not issuer.startswith("https://"):
            raise ValueError("MCP_AUTH_ISSUER must use HTTPS")
        if not audience.startswith("https://"):
            raise ValueError("MCP_RESOURCE_SERVER_URL must use HTTPS")
        if not algorithms:
            raise ValueError("at least one JWT algorithm is required")

        self.jwks_url = jwks_url
        self.issuer = issuer.rstrip("/")
        self.audience = audience
        self.algorithms = algorithms
        self._jwk_client = PyJWKClient(jwks_url)

    async def verify_token(self, token: str) -> AccessToken | None:
        if not token or token.count(".") != 2:
            return None

        try:
            signing_key = await asyncio.to_thread(
                self._jwk_client.get_signing_key_from_jwt, token
            )
            claims: dict[str, Any] = await asyncio.to_thread(
                jwt.decode,
                token,
                signing_key.key,
                algorithms=list(self.algorithms),
                audience=self.audience,
                issuer=self.issuer,
                options={
                    "require": ["exp", "iat", "iss", "aud"],
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_iat": True,
                    "verify_iss": True,
                    "verify_aud": True,
                },
            )
        except Exception as exc:  # noqa: BLE001
            # Do not log token contents or exception messages because JWT libraries
            # and HTTP clients can include sensitive request material in errors.
            logger.info("MCP bearer token rejected: %s", type(exc).__name__)
            return None

        scopes = self._scopes(claims)
        subject = claims.get("sub")
        client_id = str(claims.get("azp") or claims.get("client_id") or subject or "unknown")
        return AccessToken(
            token=token,
            client_id=client_id,
            subject=str(subject) if subject is not None else None,
            scopes=scopes,
            expires_at=claims.get("exp"),
            resource=self.audience,
            claims=claims,
        )

    @staticmethod
    def _scopes(claims: dict[str, Any]) -> list[str]:
        value = claims.get("scope") or claims.get("scp") or []
        if isinstance(value, str):
            return value.split()
        if isinstance(value, (list, tuple, set)):
            return [str(item) for item in value]
        return []
