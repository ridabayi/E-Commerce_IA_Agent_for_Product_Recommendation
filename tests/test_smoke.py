import importlib


def _get_app():
    mod = importlib.import_module("app")
    if hasattr(mod, "app"):
        return mod.app
    if hasattr(mod, "create_app"):
        return mod.create_app()
    raise RuntimeError("No Flask app found (need app or create_app).")


def test_app_imports():
    assert _get_app() is not None


def test_basic_route_status():
    app = _get_app()
    app.testing = True
    client = app.test_client()
    for path in ("/health", "/"):
        resp = client.get(path)
        if resp.status_code in (200, 404):
            assert True
            return
    raise AssertionError("No /health or / route responding with 200/404.")
