from pathlib import Path


def test_version_20_23():
    text = Path('scripts/marsel_api_inventory_v20_23.py').read_text(encoding='utf-8')
    assert 'VERSION = "20.23"' in text
