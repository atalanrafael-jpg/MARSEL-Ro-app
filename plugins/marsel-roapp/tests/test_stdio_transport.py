from __future__ import annotations

import asyncio
import os
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


SERVER = Path(__file__).resolve().parents[1] / "mcp_server" / "server.py"


async def _handshake() -> tuple[str | None, list[str]]:
    env = {
        "PATH": os.environ.get("PATH", ""),
        "PYTHONPATH": os.environ.get("PYTHONPATH", ""),
        "ROAPP_BASE_URL": "https://api.roapp.io/v2",
        "ROAPP_TIMEOUT_SECONDS": "5",
    }
    params = StdioServerParameters(
        command=os.environ.get("PYTHON", "python"),
        args=[str(SERVER)],
        env=env,
    )

    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            result = await session.initialize()
            tools = await session.list_tools()
            return result.server_info.name if result.server_info else None, [
                tool.name for tool in tools.tools
            ]


def test_local_mcp_stdio_handshake() -> None:
    server_name, tool_names = asyncio.run(_handshake())
    assert server_name == "MARSEL RO App"
    assert set(tool_names) >= {
        "get_orders",
        "audit_orders",
        "connector_readiness",
    }
