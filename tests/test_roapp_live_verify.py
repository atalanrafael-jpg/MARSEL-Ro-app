from agent_runtime.adapters.roapp_live_verify import verify_read

def test_missing_token_blocks_without_network(monkeypatch):
 monkeypatch.delenv("ROAPP_API_TOKEN",raising=False)
 r=verify_read("/verified-endpoint")
 assert r["status"]=="BLOCKED" and r["network_calls"]==0
