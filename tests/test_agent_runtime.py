from agent_runtime.policy import authorize
from agent_runtime.runtime import handle

def test_read_allowed(): assert authorize("read").allowed is True

def test_write_blocked(): assert authorize("write").allowed is False

def test_runtime_invariant():
 r=handle({"task_id":"t1","action":"analyze"})
 assert r["write_requests_made"]==0 and r["ro_app_data_mutated"] is False
