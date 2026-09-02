import pytest
from agent_runtime.schema import validate_task
from agent_runtime.dry_run import execute

def test_schema_rejects_unknown_action():
    with pytest.raises(ValueError): validate_task({"task_id":"x","action":"invent"})
def test_dry_run_never_mutates():
    r=execute([{ "action":"write" }])
    assert r["writes_executed"]==0 and r["result"]=="NO_MUTATION"
