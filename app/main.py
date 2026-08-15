from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import RedirectResponse
from .audit import audit_order_pages
from .config import settings
from .gmail_oauth import gmail_oauth
from .roapp_client import RoAppClient

app = FastAPI(title="MARSEL RO App Connector", version="0.4.0")


@app.get("/health")
def health():
    return {"status": "ok", "service": "marsel-roapp-connector", "version": "0.4.0"}


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


@app.get("/gmail/status")
def gmail_status():
    return gmail_oauth.status()


@app.get("/gmail/connect")
def gmail_connect(request: Request):
    """Start Google OAuth. The browser must be redirected to Google's consent page."""
    redirect_uri = str(request.url_for("gmail_callback"))
    try:
        url = gmail_oauth.authorization_url(redirect_uri)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail="Gmail OAuth is not configured") from exc
    return RedirectResponse(url=url, status_code=302)


@app.get("/gmail/callback", name="gmail_callback")
def gmail_callback(code: str | None = None, state: str | None = None, error: str | None = None):
    if error:
        raise HTTPException(status_code=400, detail="Google authorization was denied")
    if not code or not state:
        raise HTTPException(status_code=400, detail="Missing OAuth callback parameters")
    try:
        return gmail_oauth.handle_callback(code, state)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid or expired OAuth state") from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Gmail OAuth exchange failed") from exc


@app.get("/gmail/messages")
def gmail_messages(max_results: int = Query(10, ge=1, le=100)):
    """Read-only smoke-test endpoint; returns Gmail message IDs only."""
    try:
        return {"status": "ok", "messages": gmail_oauth.list_messages(max_results)}
    except PermissionError as exc:
        raise HTTPException(status_code=401, detail="Gmail is not connected") from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Gmail API request failed") from exc


@app.post("/gmail/disconnect")
def gmail_disconnect():
    gmail_oauth.disconnect()
    return {"status": "disconnected", "email": "atalanrafael@gmail.com"}
