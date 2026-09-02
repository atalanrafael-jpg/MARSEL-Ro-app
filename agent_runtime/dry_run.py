def execute(plan:list[dict])->dict:
    return {"mode":"DRY_RUN","steps":len(plan),"writes_executed":0,"deletes_executed":0,"result":"NO_MUTATION"}
