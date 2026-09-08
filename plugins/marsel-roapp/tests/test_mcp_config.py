from __future__ import annotations

import json
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = PLUGIN_ROOT / ".mcp.json"
SERVER_PATH = PLUGIN_ROOT / "mcp_server" / "server.py"


def test_codex_mcp_config_declares_expected_read_only_server() -> None:
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    server = config["mcpServers"]["marsel_roapp"]

    assert server["command"] == "uv"
    assert server["args"] == ["run", "--directory", "./mcp_server", "server.py"]
    assert server["env_vars"] == [
        "ROAPP_API_KEY",
        "ROAPP_BASE_URL",
        "ROAPP_TIMEOUT_SECONDS",
    ]
    assert SERVER_PATH.is_file()


def test_codex_mcp_relative_working_directory_is_plugin_local() -> None:
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    args = config["mcpServers"]["marsel_roapp"]["args"]

    directory = args[args.index("--directory") + 1]
    target = (PLUGIN_ROOT / directory).resolve()

    assert directory == "./mcp_server"
    assert target == (PLUGIN_ROOT / "mcp_server").resolve()
    assert (target / "server.py").is_file()
