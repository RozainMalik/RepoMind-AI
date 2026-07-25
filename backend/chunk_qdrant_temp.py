from pathlib import Path

from app.services.chunking_service import ChunkingService
from app.services.embedding_service import EmbeddingService
from app.services.qdrant_service import QdrantService

chunker = ChunkingService()
embedder = EmbeddingService()
qdrant = QdrantService()

qdrant.create_collection()

chunks = chunker.chunk_file(
    Path("repositories/flask/src/flask/app.py")
)

embedding = embedder.embed_chunk(chunks[0])

qdrant.store_chunk(
    chunks[0],
    embedding,
)

print("Stored successfully!")