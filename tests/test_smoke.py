import importlib
import os


def _get_app():
    os.environ["APP_TESTING"] = "1"
    mod = importlib.import_module("app")
    if hasattr(mod, "create_app"):
        return mod.create_app()
    if hasattr(mod, "app"):
        return mod.app
    raise RuntimeError("No Flask app found.")


def test_app_imports():
    assert _get_app() is not None


def test_basic_route_status():
    app = _get_app()
    app.testing = True
    client = app.test_client()
    assert client.get("/health").status_code == 200
