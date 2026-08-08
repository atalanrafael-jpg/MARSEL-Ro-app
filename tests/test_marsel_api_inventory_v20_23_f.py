from pathlib import Path


def test_v20_23_read_only_contract():
    text = Path('scripts/marsel_api_inventory_v20_23.py').read_text(encoding='utf-8')
    assert 'VERSION = "20.23"' in text
    assert 'method="GET"' in text
    assert 'ro_app_data_mutated' in text
