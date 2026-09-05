from dataclasses import dataclass

@dataclass(frozen=True)
class Agent:
    agent_id: str
    domain: str
    permissions: frozenset[str]

class AgentRegistry:
    def __init__(self): self._agents = {}
    def register(self, agent: Agent): self._agents[agent.agent_id] = agent
    def get(self, agent_id: str) -> Agent: return self._agents[agent_id]
