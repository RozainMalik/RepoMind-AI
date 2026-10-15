# # here the embedding model will convert the text form the repo to the vector, that's it....from sentence_transformers import SentenceTransformer
# from functools import lru_cache

# from sentence_transformers import SentenceTransformer
# from app.schemas.chunk import CodeChunk


# class EmbeddingService:

#     def __init__(self):
#         self.model = SentenceTransformer(
#             "BAAI/bge-small-en-v1.5"
#         )

#     def embed_chunks(
#         self,
#         chunks: list[CodeChunk],
#     ) -> list[list[float]]:

#         if not chunks:
#             return []

#         texts = [chunk.content for chunk in chunks]

#         embeddings = self.model.encode(
#             texts,
#             batch_size=64,
#             normalize_embeddings=True,
#             show_progress_bar=True,
#         )

#         return embeddings.tolist()

#     def embed_query(self, query):
#         return self.model.encode(
#             query,
#             normalize_embeddings=True
#         )


# @lru_cache(maxsize=1)
# def get_embedding_service() -> EmbeddingService:
#     # Load the model ONCE per process and share it between indexing and
#     # retrieval, instead of reloading it from disk on every index job
#     return EmbeddingService()


from functools import lru_cache

from sentence_transformers import SentenceTransformer

from app.schemas.chunk import CodeChunk


class EmbeddingService:

    def __init__(self):
        self.model = SentenceTransformer(
            "BAAI/bge-small-en-v1.5"
        )

    def embed_chunks(
        self,
        chunks: list[CodeChunk],
    ) -> list[list[float]]:

        if not chunks:
            return []

        texts = [chunk.content for chunk in chunks]

        embeddings = self.model.encode(
            texts,
            batch_size=64,
            normalize_embeddings=True,
            show_progress_bar=True,
        )

        return embeddings.tolist()

    def embed_query(self, query):
        return self.model.encode(
            query,
            normalize_embeddings=True,
        )


@lru_cache(maxsize=1)
def get_embedding_service() -> EmbeddingService:
    # Load the model ONCE per process and share it between indexing and
    # retrieval, instead of reloading it from disk on every index job
    return EmbeddingService()