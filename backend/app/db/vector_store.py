import os
import chromadb
from typing import List, Dict, Any

class BioVectorStore:
    def __init__(self, persist_directory="./chroma_db"):
        self.persist_directory = persist_directory
        self.client = None
        self.collection = None
        
        try:
            self.client = chromadb.PersistentClient(path=self.persist_directory)
            self.collection = self.client.get_or_create_collection(
                name="biologics_knowledge",
                metadata={"hnsw:space": "cosine"}
            )
        except Exception as e:
            print(f"Failed to initialize ChromaDB: {e}")
            
    def add_documents(self, documents: List[str], metadatas: List[Dict[str, Any]], ids: List[str]):
        """Adds scientific texts to the vector store."""
        if not self.collection: return
        try:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
        except Exception as e:
            print(f"Error adding to Vector Store: {e}")
            
    def query(self, query_text: str, n_results=5):
        """Retrieves top context for RAG."""
        if not self.collection: return []
        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
            return results["documents"][0] if results["documents"] else []
        except Exception as e:
            print(f"Error querying Vector Store: {e}")
            return []

# Singleton instance
vector_store = BioVectorStore()
