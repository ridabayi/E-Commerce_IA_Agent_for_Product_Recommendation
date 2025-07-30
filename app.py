from flask import render_template, Flask, request, Response
from prometheus_client import Counter, generate_latest
from ebay_agent.Data_ingestion import DataIngestor
from ebay_agent.rag_chain import RAGChainBuilder
from ebay_agent.vault_api_keys import *
import traceback


REQUEST_COUNT = Counter("http_requests_total", "Total HTTP Requests")
def create_app():
    app = Flask(__name__)

    # Chargement du vecteur store et de la chaîne RAG
    vector_store = DataIngestor().ingest(load_existing=True)
    rag_chain = RAGChainBuilder(vector_store).build_chain()

    @app.route("/")
    def index():
        REQUEST_COUNT.inc()
        return render_template("index.html")

    @app.route("/get", methods=["POST"])
    def get_response():
        try:
            user_input = request.form["msg"]
            session_id = request.form.get("session_id", "default-session")
            print(f"[User Input] {user_input} | Session: {session_id}")

            response = rag_chain.invoke(
                {"input": user_input},
                config={"configurable": {"session_id": session_id}}
            )["answer"]

            return str(response)

        except Exception as e:
            print("❌ Erreur dans /get:", e)
            traceback.print_exc()
            return "Une erreur est survenue côté serveur."

    @app.route("/metrics")
    def metrics():
        return Response(generate_latest(), mimetype="text/plain")

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
