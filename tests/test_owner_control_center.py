from scripts.marsel_owner_control_center import item, snapshot


def test_invalid_status_fails_closed():
    try:
        item(
            area="CI",
            status="GREEN",
            evidence_class="VERIFIED DOCUMENTATION",
            message="invalid",
            next_step="review",
        )
    except ValueError as exc:
        assert "Unsupported status" in str(exc)
    else:
        raise AssertionError("invalid status must be rejected")


def test_snapshot_is_read_only_and_counts_statuses():
    data = snapshot(
        [
            item(
                area="CI",
                status="VERIFIED",
                evidence_class="VERIFIED LIVE DATA",
                message="checks passed",
                next_step="continue",
            ),
            item(
                area="Production Write",
                status="BLOCKED",
                evidence_class="PROJECT CONFIGURATION",
                message="write disabled",
                next_step="remain disabled",
            ),
        ]
    )
    assert data["mode"] == "READ_ONLY"
    assert data["production_write_authorized"] is False
    assert data["ro_app_data_mutated"] is False
    assert data["status_counts"]["VERIFIED"] == 1
    assert data["status_counts"]["BLOCKED"] == 1
