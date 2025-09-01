import importlib
import os


def _client():
    os.environ["APP_TESTING"] = "1"
    app = importlib.import_module("app").create_app()
    app.testing = True
    return app.test_client()


def test_ask_missing_body():
    c = _client()
    r = c.post("/ask")  # pas de JSON
    assert r.status_code == 400


def test_ask_non_string_question():
    c = _client()
    r = c.post("/ask", json={"question": 123})
    assert r.status_code == 400  # si tu ne gères pas encore, voir patch ci-dessous
