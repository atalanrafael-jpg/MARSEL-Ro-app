from dataclasses import dataclass
from typing import Any

ALLOWED_ACTIONS={"read","analyze","plan","dry_run","report","write","delete","sync"}
@dataclass(frozen=True)
class Task:
    task_id:str
    action:str
    payload:dict[str,Any]
    production:bool=True

def validate_task(raw:dict[str,Any])->Task:
    if not isinstance(raw,dict): raise ValueError("task must be an object")
    task_id=raw.get("task_id")
    action=raw.get("action")
    if not isinstance(task_id,str) or not task_id.strip(): raise ValueError("task_id is required")
    if action not in ALLOWED_ACTIONS: raise ValueError("unverified action")
    payload=raw.get("payload",{})
    if not isinstance(payload,dict): raise ValueError("payload must be an object")
    return Task(task_id,action,payload,bool(raw.get("production",True)))
