from pathlib import Path

from app.services.chunking_service import ChunkingService
from app.services.embedding_service import EmbeddingService
from app.services.parser_service import ParserService
from app.services.qdrant_service import QdrantService


class IndexingService:
    def __init__(self):
        self.parser = ParserService()
        self.chunker = ChunkingService()
        self.embedder = EmbeddingService()
        self.qdrant = QdrantService()

    def index_repository(self, repository_path: str, repository_id: int):
        print("=" * 60)
        print(f"INDEXING STARTED (repository {repository_id})")
        print("=" * 60)

        files = self.parser.get_source_files(repository_path)
        print(f"Files found: {len(files)}")

        chunks = []

        for file in files:
            chunks.extend(
                self.chunker.chunk_file(
                    file,
                    Path(repository_path),
                    repository_id,
                )
            )
        print(f"Chunks created: {len(chunks)}")

        # An empty index must not look like success
        if not chunks:
            raise ValueError("No supported source files found in this repository.")

        embeddings = self.embedder.embed_chunks(chunks)
        print(f"Embeddings generated: {len(embeddings)}")

        self.qdrant.store_chunks(chunks, embeddings)
        print("Stored successfully in Qdrant")

        return {
            "files_indexed": len(files),
            "chunks_created": len(chunks),
            "vectors_stored": len(embeddings),
        }