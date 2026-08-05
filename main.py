from fastapi import FastAPI, HTTPException, Query
from .roapp_client import RoAppClient

app = FastAPI(title="MARSEL RO App Connector", version="0.1.0")

@app.get("/health")
def health():
    return {"status": "ok", "service": "marsel-roapp-connector"}

@app.get("/roapp/orders")
async def orders(page: int = Query(1, ge=1)):
    try:
        return await RoAppClient().get_orders(page)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"RO App API error: {e}")
