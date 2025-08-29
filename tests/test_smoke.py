import importlib
import os


def _app():
    os.environ["APP_TESTING"] = "1"
    return importlib.import_module("app").create_app()


def test_app_imports():
    assert _app() is not None


def test_health_ok():
    client = _app().test_client()
    assert client.get("/health").status_code == 200
