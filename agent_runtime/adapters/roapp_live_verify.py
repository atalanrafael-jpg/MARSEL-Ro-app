import os
from urllib.parse import urljoin
from urllib.request import Request, urlopen
from .roapp_contract import describe

class RoAppLiveVerificationError(RuntimeError): pass

def verify_read(endpoint:str, timeout:int=10)->dict:
    contract=describe()
    if contract["status"]!="DOCUMENTED_NOT_LIVE_VERIFIED":
        raise RoAppLiveVerificationError("unexpected contract state")
    if not endpoint.startswith("/"):
        raise RoAppLiveVerificationError("endpoint must be an absolute API path")
    token=os.environ.get("ROAPP_API_TOKEN")
    if not token:
        return {"status":"BLOCKED","reason":"ROAPP_API_TOKEN not present","network_calls":0}
    url=urljoin(contract["base_url"]+"/", endpoint.lstrip("/"))
    request=Request(url,headers={"Authorization":f"Bearer {token}","Accept":"application/json"},method="GET")
    try:
        with urlopen(request,timeout=timeout) as response:
            return {"status":"LIVE_READ_RESPONSE","http_status":response.status,"network_calls":1,"data_mutated":False}
    except Exception as exc:
        return {"status":"FAILED","error_type":type(exc).__name__,"network_calls":1,"data_mutated":False}
