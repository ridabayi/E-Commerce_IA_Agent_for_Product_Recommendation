import importlib
import os


def _client():
    os.environ["APP_TESTING"] = "1"
    app = importlib.import_module("app").create_app()
    app.testing = True
    return app.test_client()


def test_security_headers_present_on_root():
    c = _client()
    r = c.get("/")
    assert r.status_code in (200, 500)  # en CI, / peut fallback "OK"
    # vérifie les headers posés par after_request
    assert r.headers.get("X-Content-Type-Options") == "nosniff"
    assert r.headers.get("X-Frame-Options") == "DENY"
    assert r.headers.get("Referrer-Policy") == "no-referrer"
    assert "default-src" in (r.headers.get("Content-Security-Policy") or "")
