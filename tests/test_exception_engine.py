from scripts.marsel_exception_engine import classify, summarize


def test_classify_fails_closed_on_unknown_category():
    try:
        classify(code="X", message="x", category="UNKNOWN")
    except ValueError:
        return
    raise AssertionError("unknown category must fail closed")


def test_summary_is_read_only():
    record = classify(code="DUP-001", message="duplicate candidate", category="DUPLICATE", severity="HIGH", evidence_class="VERIFIED_LIVE_DATA")
    result = summarize([record])
    assert result["mode"] == "READ_ONLY"
    assert result["write_requests_made"] == 0
    assert result["ro_app_data_mutated"] is False
    assert result["severity_counts"]["HIGH"] == 1
    assert result["category_counts"]["DUPLICATE"] == 1
