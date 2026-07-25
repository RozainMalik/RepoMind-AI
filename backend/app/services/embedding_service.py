# here the embedding model will convert the text form the repo to the vector, that's it....from sentence_transformers import SentenceTransformer
from sentence_transformers import SentenceTransformer
from app.schemas.chunk import CodeChunk


class EmbeddingService:

    def __init__(self):
        self.model = SentenceTransformer(
            "BAAI/bge-small-en-v1.5"
        )

    def embed_chunk(self, chunk: CodeChunk) -> list[float]:
        embedding = self.model.encode(
            chunk.content,
            normalize_embeddings=True,
        )

        return embedding.tolist()
    
    def embed_chunks(
        self,
        chunks: list[CodeChunk],
    ) -> list[list[float]]:

        embeddings = []

        for chunk in chunks:
            embeddings.append(
                self.embed_chunk(chunk)
            )

        return embeddings