from pathlib import Path


def test_v20_23_is_read_only_by_contract():
    text = Path('scripts/marsel_api_inventory_v20_23.py').read_text(encoding='utf-8')
    assert 'method="GET"' in text
    assert 'write_requests_made' in text
    assert 'ro_app_data_mutated' in text
    assert 'method="POST"' not in text
    assert 'method="PUT"' not in text
    assert 'method="PATCH"' not in text
    assert 'method="DELETE"' not in text
