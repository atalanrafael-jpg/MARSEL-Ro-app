from pathlib import Path

def test_owner_app_contains_required_vertical_slice_markers():
    html = Path("web/index.html").read_text(encoding="utf-8")
    required = (
        "Вход владельца",
        "Клиент",
        "Новый ремонт",
        "Безопасная ссылка вложения",
        "repair_status_history",
        "audit_log",
    )
    for marker in required:
        assert marker in html, marker


def test_owner_app_does_not_contain_server_secrets():
    html = Path("web/index.html").read_text(encoding="utf-8")
    forbidden = ("ROAPP_API_KEY", "roapp_api_key", "marsel_internal_api_key")
    assert not any(secret in html for secret in forbidden)
