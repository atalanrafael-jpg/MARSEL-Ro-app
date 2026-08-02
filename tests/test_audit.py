from app.audit import audit_order_pages


def test_audit_detects_duplicate_ids_and_missing_status():
    payloads = [
        {"count": 2, "data": [{"id": 101, "status": "new"}, {"id": 102}]},
        {"count": 2, "data": []},
    ]

    result = audit_order_pages(payloads)

    assert result["read_only"] is True
    assert result["orders_scanned"] == 2
    assert result["duplicate_identifiers"] == []
    assert result["missing_common_fields"]["status"] == 1


def test_audit_detects_duplicates():
    result = audit_order_pages([
        {"data": [{"id": 101}, {"id": 101}]},
    ])

    assert result["duplicate_identifiers"] == ["101"]
