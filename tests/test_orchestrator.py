from agent_runtime.orchestrator import MasterOrchestrator

def test_read_task_is_controlled():
 r=MasterOrchestrator().run({"task_id":"read-1","action":"read"})
 assert r["allowed"] is True and r["ro_app_data_mutated"] is False

def test_write_task_is_blocked():
 r=MasterOrchestrator().run({"task_id":"write-1","action":"write"})
 assert r["allowed"] is False and r["status"]=="BLOCKED"

def test_dry_run_executes_without_mutation():
 r=MasterOrchestrator().run({"task_id":"dry-1","action":"dry_run","payload":{"plan":[{"action":"write"}]}})
 assert r["dry_run"]["writes_executed"]==0
