from langchain_astradb import AstraDBVectorStore
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from ebay_agent.Data_converter import DataConverter
from ebay_agent.config import Config


class DataIngestor:
    def __init__(self):
        # Initialisation du modèle d'embedding Hugging Face
        self.embedding = HuggingFaceEndpointEmbeddings(model=Config.EMBEDDING_MODEL)

        # Connexion au vecteur store AstraDB
        self.vstore = AstraDBVectorStore(
            embedding=self.embedding,
            collection_name="amazon_product_reviews",
            api_endpoint=Config.ASTRADB_API_ENDPOINT,
            token=Config.ASTRADB_APPLICATION_TOKEN,
            namespace=Config.ASTRADB_KEYSPACE
        )

    def ingest(self, load_existing=True):
        if load_existing:
            return self.vstore

        # Conversion du CSV en liste de documents LangChain
        docs = DataConverter("Data/ebay_reviews.csv").convert()

        # Ajout au vectorstore
        self.vstore.add_documents(docs)

        return self.vstore
