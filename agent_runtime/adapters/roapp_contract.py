from ..contracts import ROAPP_PUBLIC_API

def describe()->dict:
    return {
        "base_url":ROAPP_PUBLIC_API.base_url,
        "auth_scheme":ROAPP_PUBLIC_API.auth_scheme,
        "rate_limit_rps":ROAPP_PUBLIC_API.rate_limit_rps,
        "page_size_max":ROAPP_PUBLIC_API.page_size_max,
        "mode":"READ_ONLY",
        "live_calls":0,
        "status":"DOCUMENTED_NOT_LIVE_VERIFIED",
    }
