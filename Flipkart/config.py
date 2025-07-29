import os
from Flipkart import vault_env


class Config:
    ASTRADB_API_ENDPOINT = os.environ.get("ASTRADB_API_ENDPOINT")
    ASTRADB_APPLICATION_TOKEN = os.environ.get("ASTRADB_APPLICATION_TOKEN")
    ASTRADB_KEYSPACE = os.environ.get("ASTRADB_KEYSPACE")      
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
    EMBEDDING_MODEL = "BAAI/bge-base-en-v1.5" 
    RAG_MODEL = "llama-3.1-8b-instant"
     