from flask import render_template, Flask, request, Response
from prometheus_client import Counter, generate_latest
from ebay_agent.Data_ingestion import DataIngestor
from ebay_agent.rag_chain import RAGChainBuilder
from dotenv import load_dotenv
load_dotenv()
import traceback
import markdown  

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

            # 🔁 Appel de la chaîne RAG
            response_raw = rag_chain.invoke(
                {"input": user_input},
                config={"configurable": {"session_id": session_id}}
            )["answer"]

            # ✅ Convertir la réponse Markdown → HTML (gras, sauts de ligne, bullets…)
            response_html = markdown.markdown(response_raw, output_format="html5")

            return response_html

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
