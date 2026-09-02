from .schema import validate_task
from .policy import authorize
from .audit import evidence
from .dry_run import execute

class MasterOrchestrator:
    def run(self, raw:dict)->dict:
        task=validate_task(raw)
        decision=authorize(task.action, task.production)
        record=evidence(task.task_id,task.action,decision.status,{"reason":decision.reason})
        result={"task_id":task.task_id,"status":decision.status,"allowed":decision.allowed,"evidence":record,"write_requests_made":0,"ro_app_data_mutated":False}
        if decision.allowed and task.action=="dry_run":
            result["dry_run"]=execute(task.payload.get("plan",[]))
        return result
