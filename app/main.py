from __future__ import annotations

import secrets
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import Depends, FastAPI, Header, HTTPException, Query

from .audit import audit_order_pages
from .config import settings
from .mcp_auth import JWTTokenVerifier
from .mcp_server import create_mcp_server
from .roapp_client import RoAppClient


mcp_http = None

if settings.mcp_http_enabled:
    missing = [
        name
        for name, value in (
            ("MCP_RESOURCE_SERVER_URL", settings.mcp_resource_server_url),
            ("MCP_AUTH_ISSUER", settings.mcp_auth_issuer),
            ("MCP_AUTH_JWKS_URL", settings.mcp_auth_jwks_url),
        )
        if not value
    ]
    if missing:
        raise RuntimeError(
            "MCP HTTP mode requires: " + ", ".join(missing)
        )

    verifier = JWTTokenVerifier(
        jwks_url=settings.mcp_auth_jwks_url,
        issuer=settings.mcp_auth_issuer,
        audience=settings.mcp_resource_server_url,
    )
    mcp_http = create_mcp_server(verifier)
    mcp_http.settings.streamable_http_path = "/"


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    if mcp_http is None:
        yield
        return

    async with mcp_http.session_manager.run():
        yield


app = FastAPI(
    title="MARSEL RO App Connector",
    version="0.4.1",
    lifespan=lifespan,
)

if mcp_http is not None:
    app.mount("/mcp", mcp_http.streamable_http_app())


def require_internal_auth(x_marsel_api_key: str | None = Header(default=None)) -> None:
    """Authorize callers to the MARSEL connector without exposing RO App credentials."""
    configured = settings.marsel_internal_api_key
    if not configured:
        raise HTTPException(status_code=503, detail="MARSEL connector authentication is not configured")
    if not x_marsel_api_key or not secrets.compare_digest(x_marsel_api_key, configured):
        raise HTTPException(status_code=401, detail="Unauthorized")


@app.get("/health")
def health():
    return {"status": "ok", "service": "marsel-roapp-connector", "version": app.version}


@app.get("/ready")
def ready():
    """Non-sensitive service readiness check; never reports secret presence."""
    return {
        "status": "ready" if settings.roapp_base_url else "not_configured",
        "service": "marsel-roapp-connector",
        "version": app.version,
        "mcp_http_enabled": settings.mcp_http_enabled,
    }


@app.get("/roapp/orders", dependencies=[Depends(require_internal_auth)])
async def orders(page: int = Query(1, ge=1)):
    try:
        return await RoAppClient().get_orders(page)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail="RO App API temporarily unavailable") from exc
    except Exception as exc:
        # Do not expose upstream URLs, exception text, or configuration details
        # through the public API response.
        raise HTTPException(status_code=502, detail="RO App API request failed") from exc


@app.get("/roapp/audit/orders", dependencies=[Depends(require_internal_auth)])
async def audit_orders(max_pages: int = Query(10, ge=1, le=100)):
    """Read-only audit of order pages; no RO App data is changed."""
    try:
        pages = await RoAppClient().get_orders_pages(max_pages)
        return audit_order_pages(pages)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail="RO App API temporarily unavailable") from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail="RO App API audit failed") from exc
