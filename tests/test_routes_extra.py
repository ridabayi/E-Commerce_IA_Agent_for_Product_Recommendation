import importlib
import os
from unittest.mock import Mock


def _app(testing="1"):
    os.environ["APP_TESTING"] = testing  # "1" disables RAG; "0" enables RAG path
    app = importlib.import_module("app").create_app()
    app.testing = True
    return app


def test_health_ok():
    c = _app("1").test_client()
    r = c.get("/health")
    assert r.status_code == 200
    data = r.get_json()
    assert data["status"] == "ok"


def test_metrics_ok():
    c = _app("1").test_client()
    r = c.get("/metrics")
    assert r.status_code == 200
    assert r.mimetype == "text/plain"


def test_get_text_fallback_when_testing():
    c = _app("1").test_client()
    r = c.post("/get", data={"msg": "hi", "session_id": "s1"})
    assert r.status_code == 200
    assert r.mimetype == "text/plain"
    assert "hi" in r.get_data(as_text=True)


def test_ask_400_on_empty_json():
    c = _app("1").test_client()
    r = c.post("/ask", json={"question": ""})
    assert r.status_code == 400


def test_ask_200_fallback_when_testing():
    c = _app("1").test_client()
    r = c.post("/ask", json={"question": "hello"})
    assert r.status_code == 200
    body = r.get_json()
    assert "answer" in body


def test_ask_200_with_rag_mock():
    app = _app("0")  # enable non-testing path
    # inject mock RAG chain
    state = app.config["RAG_STATE"]
    state.ready = True
    mock = Mock()
    mock.invoke.return_value = {"answer": "mocked"}
    state.chain = mock

    c = app.test_client()
    r = c.post("/ask", json={"question": "hello"})
    assert r.status_code == 200
    assert r.get_json()["answer"] == "mocked"
