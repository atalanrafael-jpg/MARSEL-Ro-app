from dataclasses import dataclass
from typing import Callable

@dataclass(frozen=True)
class ToolSpec:
    name:str
    mode:str
    handler:Callable
    contract_status:str="NOT_VERIFIED"

class ToolRegistry:
    def __init__(self): self._tools={}
    def register(self,spec:ToolSpec):
        if spec.name in self._tools: raise ValueError("duplicate tool")
        if spec.mode not in {"READ_ONLY","DRY_RUN","WRITE"}: raise ValueError("invalid tool mode")
        self._tools[spec.name]=spec
    def get(self,name:str)->ToolSpec: return self._tools[name]
    def list(self): return dict(self._tools)
