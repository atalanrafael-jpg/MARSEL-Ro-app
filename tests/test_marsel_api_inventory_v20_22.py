from scripts.marsel_api_inventory_v20_22 import extract_explicit_method_paths, parse_openapi


def test_extracts_full_api_url_without_guessing():
    text = "get https://api.roapp.io/v2/orders/{order_id}/items"
    assert extract_explicit_method_paths(text) == [
        ("GET", "/v2/orders/{order_id}/items", "documentation_body")
    ]


def test_extracts_multiple_documented_operations():
    text = """
    GET https://api.roapp.io/v2/orders
    GET https://api.roapp.io/v2/orders/{order_id}
    GET https://api.roapp.io/v2/catalog/products
    """
    result = extract_explicit_method_paths(text)
    paths = {(method, path) for method, path, _ in result}
    assert ("GET", "/v2/orders") in paths
    assert ("GET", "/v2/orders/{order_id}") in paths
    assert ("GET", "/v2/catalog/products") in paths
    assert len(paths) == 3


def test_parses_only_real_openapi_paths():
    spec = {
        "openapi": "3.0.0",
        "paths": {
            "/orders": {"get": {}},
            "/orders/{order_id}": {"get": {}, "patch": {}},
        },
    }
    result = parse_openapi(__import__("json").dumps(spec))
    assert ("GET", "/v2/orders", "openapi") in result
    assert ("GET", "/v2/orders/{order_id}", "openapi") in result
    assert ("PATCH", "/v2/orders/{order_id}", "openapi") in result


def test_openapi_does_not_accept_unrelated_host_paths():
    spec = {"openapi": "3.0.0", "paths": {"https://example.com/orders": {"get": {}}}}
    assert parse_openapi(__import__("json").dumps(spec)) == []
