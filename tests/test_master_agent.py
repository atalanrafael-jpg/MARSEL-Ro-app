from app.master_agent import AgentRequest, Evidence, Mode, Status, checkpoint_dict, execute


def test_read_only_request_completes_at_checkpoint():
    state, checkpoint = execute(AgentRequest("req-1", "inventory audit"))
    assert state.status is Status.DONE
    assert state.current_step == "CHECKPOINT"
    assert checkpoint_dict(checkpoint)["state_hash"] == checkpoint.state_hash


def test_write_is_fail_closed():
    state, checkpoint = execute(AgentRequest("req-2", "sync", mode=Mode.WRITE))
    assert state.status is Status.BLOCKED
    assert state.current_step == "SAFETY_GATE"
    assert state.reason == "production_write_not_implemented"
    assert checkpoint.state_hash


def test_production_flag_is_fail_closed_even_in_read_only_mode():
    state, _ = execute(AgentRequest("req-3", "sync", production=True))
    assert state.status is Status.BLOCKED
    assert state.current_step == "SAFETY_GATE"


def test_destructive_action_is_blocked():
    state, _ = execute(AgentRequest("req-4", "delete duplicate", destructive=True))
    assert state.status is Status.BLOCKED
    assert state.reason == "destructive_action_requires_explicit_gate"


def test_unverified_evidence_blocks():
    evidence = [Evidence("ev-1", "api", False, "test-source")]
    state, _ = execute(AgentRequest("req-5", "audit"), evidence)
    assert state.status is Status.BLOCKED
    assert state.current_step == "ANALYZE"
    assert state.reason == "unverified_evidence_present"


def test_verified_evidence_is_recorded():
    evidence = [Evidence("ev-2", "api", True, "authoritative-contract")]
    state, checkpoint = execute(AgentRequest("req-6", "audit"), evidence)
    assert state.status is Status.DONE
    assert state.evidence_ids == ("ev-2",)
    assert checkpoint.evidence_ids == ("ev-2",)


def test_missing_request_id_blocks_at_validation():
    state, _ = execute(AgentRequest("", "audit"))
    assert state.status is Status.BLOCKED
    assert state.current_step == "VALIDATE"
    assert state.reason == "request_id_missing"
