#TESTING PARSER

#  from app.services.parser_service import ParserService

# parser = ParserService()

# files = parser.get_source_files("repositories/MedSPOT")

# print(f"Found {len(files)} files\n")

# for file in files[:20]:
#     print(file)


#TESTING CHUNKING
# from pathlib import Path

# from app.services.chunking_service import ChunkingService

# service = ChunkingService()

# chunks = service.chunk_file(
#     Path("repositories/flask/src/flask/app.py")
# )

# print(f"Total Chunks: {len(chunks)}")

# print()

# for chunk in chunks[:3]:
#     print("=" * 60)
#     print(f"Chunk {chunk.chunk_index}")
#     print(f"Lines: {chunk.start_line}-{chunk.end_line}")
#     print(f"Language: {chunk.language}")
#     print(chunk.content[:300])
#     print()


#TESTING EMEDDING
# from pathlib import Path

# from app.services.chunking_service import ChunkingService
# from app.services.embedding_service import EmbeddingService

# chunker = ChunkingService()
# embedder = EmbeddingService()

# chunks = chunker.chunk_file(
#     Path("repositories/flask/src/flask/app.py")
# )

# vector = embedder.embed_chunk(chunks[0])

# print(len(vector))
# print(vector[:10])

# #TESTING QDRANT
# from app.services.qdrant_service import QdrantService

# service = QdrantService()

# service.create_collection()

# print(service.client.get_collections())


# # RETREIVAL TEST
# from app.services.retrieval_service import RetrievalService


# retriever = RetrievalService()


# results = retriever.retrieve(
#     "Where are the content of .env file?"
# )


# for result in results:
#     print("\n")
#     print(result.payload["file_path"])
#     print(result.score)

# PROMPT CONSTRUCTION TEST

# from app.services.retrieval_service import RetrievalService
# from app.services.prompt_service import PromptService


# retriever = RetrievalService()
# prompt_service = PromptService()


# question = "Where is authentication implemented?"


# chunks = retriever.retrieve(
#     question,
#     limit=3
# )


# prompt = prompt_service.build_prompt(
#     question,
#     chunks
# )


# print(prompt)

# CHAT SERVICE TEST
# from app.services.chat_service import ChatService

# chat = ChatService()

# response = chat.ask("Where is authentication implemented?")

# print(response)



# FULL TEST WITH LLM
from app.services.chat_service import ChatService
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table


console = Console()

chat = ChatService()

response = chat.ask(
    "Where is authentication implemented?"
)


# Answer panel
console.print(
    Panel(
        Markdown(response["answer"]),
        title="🤖 RepoMind AI",
        border_style="cyan"
    )
)


# Sources table
table = Table(
    title="📚 Sources",
    show_header=True,
    header_style="bold magenta"
)


table.add_column("#", justify="center")
table.add_column("File")
table.add_column("Lines")
table.add_column("Score")


for i, source in enumerate(response["sources"], start=1):

    table.add_row(
        str(i),
        source["file_path"].split("/repositories/")[-1],
        f'{source["start_line"]}-{source["end_line"]}',
        f'{source["score"]:.3f}'
    )


console.print(table)