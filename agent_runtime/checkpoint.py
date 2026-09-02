def checkpoint(name:str, evidence_ids:list[str], status:str)->dict:
    return {"name":name,"evidence_ids":list(evidence_ids),"status":status}
