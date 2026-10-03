from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
)
from uuid import uuid4
from app.schemas.chunk import CodeChunk

class QdrantService:

    COLLECTION_NAME = "code_chunks"

    def __init__(self):
        self.client = QdrantClient(
            host="localhost",
            port=6333,
        )

    def create_collection(self):
        collections = self.client.get_collections()

        existing = [
            collection.name
            for collection in collections.collections
        ]

        if self.COLLECTION_NAME in existing:
            return

        self.client.create_collection(
            collection_name=self.COLLECTION_NAME,
            vectors_config=VectorParams(
                size=384,
                distance=Distance.COSINE,
            ),
        )

    def recreate_collection(self):
        collections = self.client.get_collections()
        existing = [
            collection.name
            for collection in collections.collections
        ]

        if self.COLLECTION_NAME in existing:
            self.client.delete_collection(
                collection_name=self.COLLECTION_NAME
            )

        self.create_collection()

    def store_chunks(
        self,
        chunks: list[CodeChunk],
        embeddings: list[list[float]],
    ):
        points = []

        if len(chunks) != len(embeddings):
            raise ValueError(
                "Number of chunks and embeddings must match." #if we didn't do this, zip() will resort to the shorter list, and hence the pairing will be wrong or it could be that many chunks won't be stored
            )
        
        for chunk, embedding in zip(chunks, embeddings): #zipping is used to pair each chunk with their corresponding vector..
            point = PointStruct(
                id=str(uuid4()),
                vector=embedding,
                payload={
                    "repository_id": chunk.repository_id,
                    "file_path": chunk.file_path,
                    "content": chunk.content,
                    "language": chunk.language,
                    "chunk_index": chunk.chunk_index,
                    "start_line": chunk.start_line,
                    "end_line": chunk.end_line,
                },
            )

            points.append(point)

        self.client.upsert(
            collection_name=self.COLLECTION_NAME,
            points=points,
        )

    def search(self, query_vector, repository_id: int, limit=5):

        results = self.client.query_points(
            
            collection_name="code_chunks",
            query=query_vector,
            query_filter=Filter(
                must=[
                    FieldCondition(
                        key="repository_id",
                        match=MatchValue(value=repository_id),
                    )
                ]
            ),
            limit=limit
        )

        return results.points