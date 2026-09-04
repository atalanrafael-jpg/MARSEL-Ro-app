from agent_runtime.adapters.roapp_contract import describe

def test_documented_contract_is_read_only():
 r=describe()
 assert r["base_url"]=="https://api.roapp.io/v2"
 assert r["rate_limit_rps"]==3
 assert r["page_size_max"]==50
 assert r["live_calls"]==0
