from pathlib import Path


def test_v20_23_exists():
    p = Path('scripts/marsel_api_inventory_v20_23.py')
    assert p.exists()
    text = p.read_text(encoding='utf-8')
    assert 'VERSION = "20.23"' in text
    assert 'method="GET"' in text
    assert 'write_requests_made' in text
    assert 'ro_app_data_mutated' in text
