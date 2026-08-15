from scripts.marsel_api_inventory_v20_31 import clean_preserve_parameters, strict_extract_paths


def test_clean_preserves_path_parameters():
    assert clean_preserve_parameters("`/v2/orders/{order_id}`") == "/v2/orders/{order_id}"


def test_strict_extract_requires_documented_method():
    store = {}
    strict_extract_paths("GET /v2/orders\n/v2/orders/{order_id}", "test", store)
    assert ("GET", "/v2/orders") in store
    assert ("GET", "/v2/orders/{order_id}") not in store


def test_strict_extract_accepts_explicit_method_path_pair():
    store = {}
    strict_extract_paths("GET https://api.roapp.io/v2/orders/{order_id}/items", "test", store)
    assert ("GET", "/v2/orders/{order_id}/items") in store
    assert store[("GET", "/v2/orders/{order_id}/items")]["evidence"] == "DOCUMENTATION_CONFIRMED"
