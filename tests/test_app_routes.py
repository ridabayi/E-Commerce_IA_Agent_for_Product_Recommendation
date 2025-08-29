import importlib
import os


def _client():
    os.environ["APP_TESTING"] = "1"
    app = importlib.import_module("app").create_app()
    app.testing = True
    return app.test_client()


def test_ask_invalid():
    c = _client()
    r = c.post("/ask", json={"question": ""})
    assert r.status_code == 400


def test_ask_ok():
    c = _client()
    r = c.post("/ask", json={"question": "hello"})
    assert r.status_code == 200
    assert "answer" in r.get_json()
