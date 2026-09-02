import pytest
from agent_runtime.tools import ToolRegistry,ToolSpec

def noop(): return None

def test_registry_rejects_duplicate():
 r=ToolRegistry(); r.register(ToolSpec("audit","READ_ONLY",noop))
 with pytest.raises(ValueError): r.register(ToolSpec("audit","READ_ONLY",noop))
def test_registry_rejects_invalid_mode():
 with pytest.raises(ValueError): ToolRegistry().register(ToolSpec("x","UNKNOWN",noop))
