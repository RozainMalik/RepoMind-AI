from app.services.embedding_service import EmbeddingService
from app.services.qdrant_service import QdrantService


class RetrievalService:

    def __init__(self):
        self.embedder = EmbeddingService()
        self.qdrant = QdrantService()


    def retrieve(self, question: str, limit: int = 5):

        query_vector = self.embedder.embed_query(question)

        results = self.qdrant.search(
            query_vector=query_vector,
            limit=limit
        )

        return results