from __future__ import annotations

from typing import Any

from mcp.server.auth.provider import TokenVerifier
from mcp.server.auth.settings import AuthSettings
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.server import Settings as FastMCPSettings
from pydantic import AnyHttpUrl

from .audit import audit_order_pages
from .config import settings
from .roapp_client import RoAppClient


# The MCP v1 FastMCP Settings model can retain an unresolved forward reference
# for its generic ``lifespan`` field. Recent pydantic-settings versions warn
# when that incomplete model is instantiated. Rebuild it after the MCP module
# has finished defining FastMCP; this is the upstream-documented workaround and
# does not change server lifespan behaviour.
if not FastMCPSettings.__pydantic_complete__:
    FastMCPSettings.model_rebuild()


MCP_NAME = "MARSEL RO App"
MCP_INSTRUCTIONS = (
    "Read-only access to the MARSEL RO App connector. "
    "Use these tools to inspect orders and run bounded data-quality audits. "
    "No tool exposed by this server mutates RO App data."
)


def create_mcp_server(token_verifier: TokenVerifier | None = None) -> FastMCP:
    """Create an MCP server for local stdio or authenticated HTTP use."""
    kwargs: dict[str, Any] = {
        "name": MCP_NAME,
        "instructions": MCP_INSTRUCTIONS,
        "json_response": True,
        "stateless_http": True,
    }

    if token_verifier is not None:
        if not settings.mcp_resource_server_url or not settings.mcp_auth_issuer:
            raise RuntimeError(
                "MCP_RESOURCE_SERVER_URL and MCP_AUTH_ISSUER are required for authenticated MCP HTTP mode"
            )
        kwargs["token_verifier"] = token_verifier
        kwargs["auth"] = AuthSettings(
            issuer_url=AnyHttpUrl(settings.mcp_auth_issuer),
            resource_server_url=AnyHttpUrl(settings.mcp_resource_server_url),
            required_scopes=settings.mcp_required_scopes,
        )

    mcp = FastMCP(**kwargs)

    @mcp.tool(
        annotations={
            "title": "Get RO App orders",
            "readOnlyHint": True,
            "openWorldHint": False,
        }
    )
    async def get_orders(page: int = 1) -> dict[str, Any]:
        """Fetch one bounded RO App orders page without modifying RO App data."""
        if page < 1:
            raise ValueError("page must be >= 1")
        return await RoAppClient().get_orders(page)

    @mcp.tool(
        annotations={
            "title": "Audit RO App orders",
            "readOnlyHint": True,
            "openWorldHint": False,
        }
    )
    async def audit_orders(max_pages: int = 10) -> dict[str, Any]:
        """Run a bounded read-only order data-quality audit across up to 100 pages."""
        if not 1 <= max_pages <= 100:
            raise ValueError("max_pages must be between 1 and 100")
        pages = await RoAppClient().get_orders_pages(max_pages)
        return audit_order_pages(pages)

    @mcp.tool(
        annotations={
            "title": "Check MARSEL connector readiness",
            "readOnlyHint": True,
            "openWorldHint": False,
        }
    )
    def connector_readiness() -> dict[str, Any]:
        """Report non-secret connector configuration state without contacting upstream APIs."""
        return {
            "status": "ready" if settings.roapp_api_key else "not_configured",
            "roapp_api_base_configured": bool(settings.roapp_base_url),
            "roapp_api_key_configured": bool(settings.roapp_api_key),
            "mcp_http_enabled": settings.mcp_http_enabled,
            "mcp_auth_configured": bool(
                settings.mcp_auth_issuer and settings.mcp_resource_server_url
            ),
            "required_scopes": settings.mcp_required_scopes,
        }

    return mcp


def create_local_mcp_server() -> FastMCP:
    """Create the unauthenticated local stdio server for trusted local Codex use."""
    return create_mcp_server()
