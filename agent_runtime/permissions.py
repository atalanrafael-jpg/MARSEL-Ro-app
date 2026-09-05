class PermissionEngine:
    def allowed(self, agent, action: str, risk_level: str) -> bool:
        if action in {"delete", "production_write"}: return False
        if risk_level == "CRITICAL": return False
        return action in agent.permissions
