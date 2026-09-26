from agent_runtime.registry import Agent, AgentRegistry
from agent_runtime.permissions import PermissionEngine


def test_registry_round_trip_and_permission_boundary():
    registry = AgentRegistry()
    agent = Agent("tester", "testing", frozenset({"read", "test"}))
    registry.register(agent)
    assert registry.get("tester") == agent

    engine = PermissionEngine()
    assert engine.allowed(agent, "test", "LOW") is True
    assert engine.allowed(agent, "production_write", "LOW") is False
    assert engine.allowed(agent, "delete", "LOW") is False
    assert engine.allowed(agent, "read", "CRITICAL") is False
