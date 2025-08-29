from __future__ import annotations

import logging
import traceback
from typing import Any

import markdown
from dotenv import load_dotenv
from flask import Flask, Response, jsonify, render_template, request
from prometheus_client import Counter, generate_latest

from Ecommerce_agent.Data_ingestion import DataIngestor
from Ecommerce_agent.rag_chain import RAGChainBuilder

# Charge les variables d'environnement tôt
load_dotenv()

# ---------- Logging ----------
logger = logging.getLogger("ecommerce_app")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

# ---------- Metrics ----------
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP Requests",
    ["path", "method"],
)


def create_app() -> Flask:
    """Factory Flask app."""
    app: Flask = Flask(__name__)

    # Pré-charge le vector store + RAG (fail fast)
    logger.info("Initializing vector store and RAG chain...")
    vector_store = DataIngestor().ingest(load_existing=True)
    rag_chain = RAGChainBuilder(vector_store).build_chain()
    logger.info("RAG chain ready.")

    @app.get("/")
    def index() -> str:
        REQUEST_COUNT.labels(path="/", method="GET").inc()
        return render_template("index.html")

    @app.post("/get")
    def get_response() -> Response | str:
        REQUEST_COUNT.labels(path="/get", method="POST").inc()
        try:
            user_input: str = request.form["msg"]
            session_id: str = request.form.get("session_id", "default-session")
            logger.info("User input received | session=%s", session_id)

            # Appel de la chaîne RAG
            rag_input: dict[str, Any] = {"input": user_input}
            response_raw: str = rag_chain.invoke(
                rag_input, config={"configurable": {"session_id": session_id}}
            )["answer"]

            # Markdown -> HTML (pour le front)
            response_html: str = markdown.markdown(response_raw, output_format="html5")
            return response_html

        except Exception as exc:  # noqa: BLE001
            logger.exception("Error in /get: %s", exc)
            traceback.print_exc()
            return "Une erreur est survenue côté serveur."

    @app.get("/health")
    def health() -> Response:
        """Simple healthcheck pour probe/liveness."""
        REQUEST_COUNT.labels(path="/health", method="GET").inc()
        return jsonify(status="ok")

    @app.get("/metrics")
    def metrics() -> Response:
        """Prometheus scrape endpoint."""
        # Pas d'incrément ici, pour ne pas biaiser les compteurs
        return Response(generate_latest(), mimetype="text/plain")

    return app


if __name__ == "__main__":
    app_ = create_app()
    app_.run(host="0.0.0.0", port=5000, debug=True)
