from app.services.parser_service import ParserService
from app.services.chunking_service import ChunkingService
from app.services.embedding_service import EmbeddingService
from app.services.qdrant_service import QdrantService

class IndexingService:
    def __init__(self):
        self.parser = ParserService()
        self.chunker = ChunkingService()
        self.embedder = EmbeddingService()
        self.qdrant = QdrantService()


    def index_repository(self, repository_path: str,):
        print("=" * 60)
        print("INDEXING STARTED")
        print("=" * 60)


        files = self.parser.get_source_files(repository_path)
        print(f"Files found: {len(files)}")

        chunks = []

        for file in files:
            chunks.extend(self.chunker.chunk_file(file))
        print(f"Chunks created: {len(chunks)}")


        embeddings = self.embedder.embed_chunks(chunks)
        print(f"Embeddings generated: {len(embeddings)}") 

        self.qdrant.store_chunks(chunks, embeddings,)
        print("Stored successfully in Qdrant")

        return {
            "files_indexed": len(files),
            "chunks_created": len(chunks),
            "vectors_stored": len(embeddings),
        }
        