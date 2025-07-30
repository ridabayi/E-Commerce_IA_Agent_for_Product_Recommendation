import pandas as pd
from langchain_core.documents import Document

class DataConverter:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def convert(self):
        # Lecture du CSV
        df = pd.read_csv(self.file_path)

        # Renommer pour simplifier l'accès
        df = df.rename(columns={
            "review title": "title",
            "review content": "review"
        })

        # Nettoyage : ignorer les lignes vides
        df = df[df["review"].notnull() & df["title"].notnull()]
        df = df[df["review"].str.strip() != ""]

        # Conversion en documents LangChain
        docs = []
        for _, row in df.iterrows():
            content = row["review"].strip()
            metadata = {
                "title": row["title"].strip(),
                "category": row["category"].strip()
            }
            docs.append(Document(page_content=content, metadata=metadata))

        return docs
