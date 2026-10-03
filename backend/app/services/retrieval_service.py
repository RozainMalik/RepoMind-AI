from app.services.embedding_service import EmbeddingService
from app.services.qdrant_service import QdrantService


class RetrievalService:

    def __init__(self):
        self.embedder = EmbeddingService()
        self.qdrant = QdrantService()

    def retrieve(
        self,
        question: str,
        repository_id: int,
        limit: int = 5
    ):
        query_vector = self.embedder.embed_query(question)

        # Retrieve more candidates because some will be filtered out
        results = self.qdrant.search(
            query_vector=query_vector,
            repository_id=repository_id,
            limit=20
        )

        filtered_results = []

        ignored = [
            "tests/",
            ".github/",
            "HISTORY.md"
        ]

        for result in results:
            file_path = result.payload["file_path"]

            if any(x in file_path for x in ignored):
                continue

            filtered_results.append(result)

            if len(filtered_results) >= limit:
                break

        return filtered_results