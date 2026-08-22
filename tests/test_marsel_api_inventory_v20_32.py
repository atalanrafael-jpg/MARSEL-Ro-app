from scripts.marsel_api_inventory_v20_32 import clean_preserve_parameters, strict_extract_paths


def test_active_inventory_imports_as_package():
    assert callable(clean_preserve_parameters)
    assert callable(strict_extract_paths)


def test_active_inventory_preserves_path_parameters():
    assert clean_preserve_parameters("`/v2/orders/{order_id}`") == "/v2/orders/{order_id}"


def test_active_inventory_requires_documented_method():
    store = {}
    strict_extract_paths("GET /v2/orders\n/v2/orders/{order_id}", "test", store)
    assert ("GET", "/v2/orders") in store
    assert ("GET", "/v2/orders/{order_id}") not in store
