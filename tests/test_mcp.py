import asyncio
import inspect

import pytest

from app.mcp_auth import JWTTokenVerifier
from app.mcp_server import create_local_mcp_server


def test_mcpserver_v2_transport_options_are_app_level():
    server = create_local_mcp_server()
    parameters = inspect.signature(server.streamable_http_app).parameters

    assert "stateless_http" in parameters
    assert "json_response" in parameters
    assert parameters["stateless_http"].kind is inspect.Parameter.KEYWORD_ONLY
    assert parameters["json_response"].kind is inspect.Parameter.KEYWORD_ONLY

    # MCP SDK v2 moved transport settings off the server constructor and onto
    # the HTTP app builder. Verify the production configuration is accepted.
    app = server.streamable_http_app(stateless_http=True, json_response=True)
    assert app is not None


def test_local_mcp_registers_only_read_tools():
    server = create_local_mcp_server()
    tools = server._tool_manager._tools
    assert set(tools) == {"get_orders", "audit_orders", "connector_readiness"}
    for tool in tools.values():
        assert tool.annotations is not None
        assert tool.annotations.readOnlyHint is True
        assert tool.annotations.openWorldHint is False


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
