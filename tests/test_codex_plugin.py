import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "marsel-roapp"


def test_codex_plugin_manifest_is_complete():
    manifest = json.loads((PLUGIN / ".codex-plugin" / "plugin.json").read_text())
    assert manifest["name"] == "marsel-roapp"
    assert manifest["version"] == "1.1.0"
    assert manifest["description"]
    assert manifest["author"]["name"]
    interface = manifest["interface"]
    for key in ("displayName", "shortDescription", "longDescription", "developerName", "category"):
        assert interface[key]
    assert interface["composerIcon"] == "./assets/icon.svg"
    assert interface["logo"] == "./assets/logo-light.svg"
    assert "[TODO:" not in json.dumps(manifest)
    assert manifest["mcpServers"] == "./.mcp.json"


def test_bundled_mcp_config_is_self_contained():
    config = json.loads((PLUGIN / ".mcp.json").read_text())
    server = config["mcpServers"]["marsel_roapp"]
    assert server["command"] == "uv"
    assert server["args"] == ["run", "--directory", "./mcp_server", "server.py"]
    assert "ROAPP_API_KEY" in server["env_vars"]
    assert "ROAPP_BASE_URL" in server["env_vars"]


def test_bundled_runtime_and_brand_assets_exist():
    for relative in (
        "mcp_server/server.py",
        "mcp_server/pyproject.toml",
        "assets/icon.svg",
        "assets/logo-light.svg",
        "assets/logo-dark.svg",
        "skills/roapp-mcp/SKILL.md",
    ):
        assert (PLUGIN / relative).is_file(), relative
