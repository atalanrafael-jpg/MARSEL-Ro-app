from dataclasses import dataclass

READ_ONLY_ACTIONS={"read","analyze","plan","dry_run","report"}
WRITE_ACTIONS={"write","delete","sync"}

@dataclass(frozen=True)
class Decision:
    allowed: bool
    status: str
    reason: str

def authorize(action:str, production:bool=True)->Decision:
    if action in READ_ONLY_ACTIONS:
        return Decision(True,"VERIFIED","Allowed in default READ_ONLY mode")
    if action in WRITE_ACTIONS and production:
        return Decision(False,"BLOCKED","Production mutation requires separate safety gate evidence")
    return Decision(False,"NOT_VERIFIED","Unknown or unverified action")
