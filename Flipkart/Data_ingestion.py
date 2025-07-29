from langchain_astradb import AstraDBVectorStore
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from Flipkart.Data_converter import DataConverter
from Flipkart.config import Config

class DataIngestion:
    def __init__(self):
        self.embeddings = HuggingFaceEndpointEmbeddings(model=Config.EMBEDDING_MODEL)
        self.vstore = AstraDBVectorStore(embedding = self.embeddings,
                                         collection_name="flipkart_database",
                                         api_endpoint=Config.ASTRADB_API_ENDPOINT,
                                         token=Config.ASTRADB_APPLICATION_TOKEN,
                                         namespace=Config.ASTRADB_KEYSPACE)
        
    def ingest_data(self, load_existing=True):
        if load_existing==True:
            return self.vstore
        
        docs = DataConverter("Data/flipkart_product_review.csv").convert()
        self.vstore.add_documents(docs)
        return self.vstore
    
if __name__ == "__main__":
    data_ingestion = DataIngestion()
    data_ingestion.ingest_data(load_existing=False)
    print("Data ingestion completed successfully.")