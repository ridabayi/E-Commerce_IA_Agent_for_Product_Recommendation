import os

from flask import Flask, Response, jsonify


def create_app() -> Flask:
    app = Flask(__name__)

    # MODE TEST (CI)
    if os.getenv("APP_TESTING") == "1":

        @app.get("/health")
        def health() -> Response:
            return jsonify(status="ok", mode="test"), 200

        @app.get("/")
        def root() -> Response:
            return jsonify(message="App running (test mode)"), 200

        return app

    # MODE NORMAL
    @app.get("/health")
    def health_prod() -> Response:
        return jsonify(status="ok", mode="prod"), 200

    @app.get("/")
    def root_prod() -> Response:
        return jsonify(message="App running"), 200

    return app


if __name__ == "__main__":  # pragma: no cover
    app = create_app()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8000")), debug=True)
