import asyncio

import pytest

from app.mcp_auth import JWTTokenVerifier
from app.mcp_server import create_local_mcp_server


def test_fastmcp_settings_model_is_complete():
    from mcp.server.fastmcp.server import Settings as FastMCPSettings

    assert FastMCPSettings.__pydantic_complete__ is True
    assert FastMCPSettings.model_fields["lifespan"]._complete is True


def test_local_mcp_registers_only_read_tools():
    server = create_local_mcp_server()
    tools = server._tool_manager._tools  # FastMCP registry; public protocol is verified by the client.
    assert set(tools) == {"get_orders", "audit_orders", "connector_readiness"}
    for tool in tools.values():
        assert tool.annotations is not None
        assert tool.annotations.readOnlyHint is True
        assert tool.annotations.openWorldHint is False


def test_mcp_http_defaults_to_stateless_mode():
    server = create_local_mcp_server()
    assert server.settings.stateless_http is True
    assert server.settings.json_response is True


def test_jwt_verifier_requires_https():
    with pytest.raises(ValueError, match="HTTPS"):
        JWTTokenVerifier(
            jwks_url="http://issuer.example.com/jwks.json",
            issuer="https://issuer.example.com/",
            audience="https://example.com/mcp",
        )


def test_jwt_verifier_rejects_non_jwt_without_network_call():
    verifier = JWTTokenVerifier(
        jwks_url="https://issuer.example.com/.well-known/jwks.json",
        issuer="https://issuer.example.com/",
        audience="https://example.com/mcp",
    )

    assert asyncio.run(verifier.verify_token("not-a-jwt")) is None
