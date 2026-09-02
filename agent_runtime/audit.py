from datetime import datetime, timezone

def evidence(task_id:str,action:str,status:str,details:dict)->dict:
    return {"timestamp":datetime.now(timezone.utc).isoformat(),"task_id":task_id,"action":action,"status":status,"details":details}
