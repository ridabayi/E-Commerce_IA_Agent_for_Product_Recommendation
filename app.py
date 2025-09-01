# app.py
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, cast

from flask import Flask, Response, jsonify, render_template, request
from flask_cors import CORS
from prometheus_client import Counter, generate_latest

from utils.logger import get_logger

logger = get_logger(__name__)

# --- Prometheus (facultatif pour les tests) ---
REQUEST_COUNT = Counter("http_requests_total", "Total HTTP Requests")

# --- RAG (Ecommerce_agent) : import seulement si dispo ---
_HAS_RAG = False
try:
    from Ecommerce_agent.Data_ingestion import DataIngestor
    from Ecommerce_agent.rag_chain import RAGChainBuilder

    _HAS_RAG = True
except Exception as e:  # pragma: no cover (ex.: en CI)
    print("[WARN] RAG imports unavailable:", repr(e))
    _HAS_RAG = False


@dataclass
class RagState:
    chain: Any | None = None
    ready: bool = False


def _extract_answer(result: Any) -> str:
    if isinstance(result, str):
        return result
    if isinstance(result, dict):
        for key in ("answer", "result", "output_text", "text", "output"):
            v = result.get(key)
            if isinstance(v, str) and v.strip():
                return v
        return str(result)
    return str(result)


def create_app() -> Flask:
    """
    Exigé par les tests:
      - importlib.import_module("app").create_app()
    Routes clés pour les tests:
      - GET  /health -> 200
      - POST /ask    -> JSON in/out {"question": "..."} -> {"answer": "..."} ; 400 si invalide
    Routes utiles pour ton UI (facultatif pour tests):
      - GET  /       -> index.html si présent, sinon "OK"
      - POST /get    -> text/plain (utilisé par ton front actuel)
      - GET  /metrics
    """
    app = Flask(__name__, template_folder="templates", static_folder="static")

    CORS(app, resources={r"/ask": {"origins": ["https://ton-domaine.fr"]}})

    testing_mode = os.getenv("APP_TESTING") == "1"

    # État RAG (typé pour mypy)
    state = RagState()
    if _HAS_RAG and not testing_mode:
        try:
            vector_store = DataIngestor().ingest(load_existing=True)
            state.chain = RAGChainBuilder(vector_store).build_chain()
            state.ready = True
            logger.exception("RAG init error")
        except Exception:  # pragma: no cover
            state.chain = None
            state.ready = False
            logger.exception("RAG init error")
    app.config["RAG_STATE"] = state

    @app.before_request
    def log_request_info():
        logger.info("➡️ %s %s", request.method, request.path)

    # ---------- Routes requises par les tests ----------
    @app.get("/health")
    def health() -> Response:
        mode = "test" if testing_mode else "prod"
        return jsonify(status="ok", mode=mode), 200

    @app.post("/ask")
    def ask() -> Response:
        """
        Tests envoient: JSON {"question": "..."}
        Doit renvoyer: 200 + JSON {"answer": "..."} ; 400 si question vide.
        """
        data = request.get_json(silent=True) or {}
        q = data.get("question")
        question = q.strip() if isinstance(q, str) else ""
        if not question:
            return jsonify(error="question is required"), 400
        logger.info(f"Received question: {question}")

        st = cast(RagState, app.config.get("RAG_STATE", RagState()))

        if testing_mode or not st.ready or st.chain is None:
            # Réponse stable en mode test
            return jsonify(answer=f"echo: {question}")

        try:
            res: Any = st.chain.invoke(
                {"input": question},
                config={"configurable": {"session_id": "user-session"}},
            )
            answer = _extract_answer(res)
        except Exception as e:  # pragma: no cover
            print("[RAG CALL ERROR]", repr(e))
            answer = f"(fallback) {question}"

        return jsonify(answer=answer)

    # ---------- Routes utiles pour ton UI (non vérifiées par les tests) ----------
    @app.get("/")
    def index() -> str:
        REQUEST_COUNT.inc()
        try:
            return render_template("index.html")
        except Exception:
            return "OK"

    @app.post("/get")
    def get_response() -> Response:
        """
        Ton front envoie form-data { msg, session_id } et attend du texte.
        """
        user_input = (request.form.get("msg") or "").strip()
        session_id = request.form.get("session_id", "user-session")

        if not user_input:
            return Response("Je n'ai rien reçu 🤖", mimetype="text/plain")

        st = cast(RagState, app.config.get("RAG_STATE", RagState()))

        if testing_mode or not st.ready or st.chain is None:
            reply = f"[{session_id}] Vous avez dit: {user_input}"
            return Response(reply, mimetype="text/plain")

        try:
            res: Any = st.chain.invoke(
                {"input": user_input},
                config={"configurable": {"session_id": session_id}},
            )
            reply = _extract_answer(res)
        except Exception as e:  # pragma: no cover
            print("[RAG CALL ERROR]", repr(e))
            reply = f"[{session_id}] (fallback) {user_input}"

        return Response(reply, mimetype="text/plain")

    @app.after_request
    def set_security_headers(resp: Response) -> Response:
        # Minimal, safe defaults (tune CSP to match your CDNs used by index.html)
        resp.headers["X-Content-Type-Options"] = "nosniff"
        resp.headers["X-Frame-Options"] = "DENY"
        resp.headers["Referrer-Policy"] = "no-referrer"
        resp.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        resp.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "img-src 'self' data: https://cdn-icons-png.flaticon.com; "
            "style-src 'self' 'unsafe-inline' "
            "https://fonts.googleapis.com https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com"
        )

        return resp

    @app.get("/metrics")
    def metrics() -> Response:
        return Response(generate_latest(), mimetype="text/plain")

    return app


if __name__ == "__main__":  # pragma: no cover
    app = create_app()
    host = os.getenv("FLASK_HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "5000"))
    logger.info("Starting server on http://%s:%s", host, port)
    app.run(host=host, port=port, debug=True)
