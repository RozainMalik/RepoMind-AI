# from app.services.parser_service import ParserService

# parser = ParserService()

# files = parser.get_source_files("repositories/MedSPOT")

# print(f"Found {len(files)} files\n")

# for file in files[:20]:
#     print(file)


from pathlib import Path

from app.services.chunking_service import ChunkingService

service = ChunkingService()

chunks = service.chunk_file(
    Path("repositories/flask/src/flask/app.py")
)

print(f"Total Chunks: {len(chunks)}")

print()

for chunk in chunks[:3]:
    print("=" * 60)
    print(f"Chunk {chunk.chunk_index}")
    print(f"Lines: {chunk.start_line}-{chunk.end_line}")
    print(f"Language: {chunk.language}")
    print(chunk.content[:300])
    print()