from fastapi import FastAPI, HTTPException, Query
from .audit import audit_order_pages
from .roapp_client import RoAppClient

app = FastAPI(title="MARSEL RO App Connector", version="0.2.0")


@app.get("/health")
def health():
    return {"status": "ok", "service": "marsel-roapp-connector", "version": "0.2.0"}


@app.get("/roapp/orders")
async def orders(page: int = Query(1, ge=1)):
    try:
        return await RoAppClient().get_orders(page)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"RO App API error: {e}")


@app.get("/roapp/audit/orders")
async def audit_orders(max_pages: int = Query(10, ge=1, le=100)):
    """Read-only audit of order pages; no RO App data is changed."""
    try:
        pages = await RoAppClient().get_orders_pages(max_pages)
        return audit_order_pages(pages)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"RO App API audit error: {e}")
