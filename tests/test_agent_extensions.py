from agent_runtime.registry import Agent, AgentRegistry
from agent_runtime.permissions import PermissionEngine
from agent_runtime.events import EventDispatcher

def test_registry():
    r=AgentRegistry(); a=Agent("A","CORE",frozenset({"read"})); r.register(a); assert r.get("A")==a

def test_permissions():
    a=Agent("A","CORE",frozenset({"read"})); p=PermissionEngine(); assert p.allowed(a,"read","LOW"); assert not p.allowed(a,"delete","LOW")

def test_events():
    d=EventDispatcher(); d.subscribe("x",lambda p:p["v"]); assert d.dispatch("x",{"v":1})==[1]
