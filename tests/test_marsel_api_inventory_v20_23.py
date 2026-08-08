import json
from pathlib import Path


SCRIPT = Path('scripts/marsel_api_inventory_v20_23.py')


def load_source():
    return SCRIPT.read_text(encoding='utf-8')


def test_v20_23_script_exists_and_is_read_only():
    source = load_source()
    assert 'VERSION = "20.23"' in source
    assert 'method="GET"' in source
    assert 'write_requests_made": 0' in source
    assert 'ro_app_data_mutated": False' in source


def test_no_write_http_method_is_used_for_requests():
    source = load_source()
    assert 'method="POST"' not in source
    assert 'method="PUT"' not in source
    assert 'method="PATCH"' not in source
    assert 'method="DELETE"' not in source


def test_normalization_never_accepts_base_only_path():
    namespace = {}
    exec(source_without_main(), namespace)
    assert namespace['normalize_path']('/v2') is None
    assert namespace['normalize_path']('/v2/') is None


def source_without_main():
    source = load_source()
    marker = "if __name__ == \"__main__\":"
    return source.split(marker, 1)[0]
