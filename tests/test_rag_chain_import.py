import importlib
import os


def test_can_import_rag_chain_module():
    os.environ["APP_TESTING"] = "1"
    mod = importlib.import_module("Ecommerce_agent.rag_chain")
    assert hasattr(mod, "RAGChainBuilder")
