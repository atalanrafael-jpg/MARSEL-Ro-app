import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "marsel-roapp"


def test_codex_plugin_manifest_is_complete():
    manifest = json.loads((PLUGIN / ".codex-plugin" / "plugin.json").read_text())
    assert manifest["name"] == "marsel-roapp"
    assert manifest["version"] == "1.0.0"
    assert manifest["description"]
    assert manifest["author"]["name"]
    interface = manifest["interface"]
    for key in ("displayName", "shortDescription", "longDescription", "developerName", "category"):
        assert interface[key]
    assert "[TODO:" not in json.dumps(manifest)
    assert manifest["mcpServers"] == "./.mcp.json"


def test_bundled_mcp_config_is_stdio_only():
    config = json.loads((PLUGIN / ".mcp.json").read_text())
    server = config["mcpServers"]["marsel-roapp"]
    assert server["command"] == "python"
    assert server["args"] == ["../../mcp_server.py"]
