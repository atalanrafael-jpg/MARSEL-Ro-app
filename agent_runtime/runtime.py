from .policy import authorize

def handle(task:dict)->dict:
    action=task.get("action","analyze")
    decision=authorize(action, task.get("production",True))
    return {"task_id":task.get("task_id"),"action":action,"allowed":decision.allowed,"status":decision.status,"reason":decision.reason,"write_requests_made":0,"ro_app_data_mutated":False}
