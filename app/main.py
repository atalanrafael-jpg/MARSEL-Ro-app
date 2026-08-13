from fastapi import FastAPI, HTTPException, Query
from .audit import audit_order_pages
from .config import settings
from .roapp_client import RoAppClient

app = FastAPI(title="MARSEL RO App Connector", version="0.3.0")


@app.get("/health")
def health():
    return {"status": "ok", "service": "marsel-roapp-connector", "version": "0.3.0"}


@app.get("/ready")
def ready():
    """Configuration readiness check; does not contact or mutate RO App."""
    return {
        "status": "ready" if settings.roapp_api_key else "not_configured",
        "api_base_configured": bool(settings.roapp_base_url),
        "api_key_configured": bool(settings.roapp_api_key),
        "timeout_seconds": settings.roapp_timeout_seconds,
        "max_retries": settings.roapp_max_retries,
    }


@app.get("/roapp/orders")
async def orders(page: int = Query(1, ge=1)):
    try:
        return await RoAppClient().get_orders(page)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail="RO App API temporarily unavailable") from exc
    except Exception as exc:
        # Do not expose upstream URLs, exception text, or configuration details
        # through the public API response.
        raise HTTPException(status_code=502, detail="RO App API request failed") from exc


@app.get("/roapp/audit/orders")
async def audit_orders(max_pages: int = Query(10, ge=1, le=100)):
    """Read-only audit of order pages; no RO App data is changed."""
    try:
        pages = await RoAppClient().get_orders_pages(max_pages)
        return audit_order_pages(pages)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail="RO App API temporarily unavailable") from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail="RO App API audit failed") from exc
