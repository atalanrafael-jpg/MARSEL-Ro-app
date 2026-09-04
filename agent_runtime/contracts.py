from dataclasses import dataclass

@dataclass(frozen=True)
class ApiContract:
    base_url:str
    auth_scheme:str
    rate_limit_rps:int
    page_size_max:int
    status:str

ROAPP_PUBLIC_API=ApiContract(
    base_url="https://api.roapp.io/v2",
    auth_scheme="Bearer Token",
    rate_limit_rps=3,
    page_size_max=50,
    status="DOCUMENTED",
)
