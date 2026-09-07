from pathlib import Path

import pytest

from scripts.marsel_production_gate_v1 import scan_text_for_secrets


def test_secret_scan_allows_configuration_presence_flag(tmp_path: Path):
    evidence = tmp_path / "evidence.json"
    evidence.write_text('{"api_key_configured": false}', encoding="utf-8")
    scan_text_for_secrets(evidence)


@pytest.mark.parametrize(
    "payload",
    [
        '{"api_key": "A" * 24}',
        '{"client_secret": "A" * 24}',
        "Be" + "arer " + "A" * 24,
        "gh" + "p_" + "A" * 24,
        "-----BEGIN " + "PRIVATE KEY-----",
    ],
)
def test_secret_scan_rejects_credential_shaped_material(tmp_path: Path, payload: str):
    # Build credential-shaped fixtures at runtime so the repository scanner never sees them as literals.
    payload = payload.replace('"A" * 24', '"' + 'A' * 24 + '"')
    evidence = tmp_path / "evidence.json"
    evidence.write_text(payload, encoding="utf-8")
    with pytest.raises(SystemExit):
        scan_text_for_secrets(evidence)
