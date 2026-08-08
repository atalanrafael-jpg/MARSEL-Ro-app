from pathlib import Path


def test_v20_23_script_present():
    text = Path('scripts/marsel_api_inventory_v20_23.py').read_text(encoding='utf-8')
    assert 'VERSION = "20.23"' in text
    assert 'never_guess_identifiers' in text
