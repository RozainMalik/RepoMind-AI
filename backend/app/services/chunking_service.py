from pathlib import Path

from app.schemas.chunk import CodeChunk


class ChunkingService:

    CHUNK_SIZE = 100
    CHUNK_OVERLAP = 20

    LANGUAGE_MAP = {
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".java": "java",
        ".cpp": "cpp",
        ".c": "c",
        ".h": "c",
        ".hpp": "cpp",
        ".go": "go",
        ".rs": "rust",
        ".md": "markdown",
        ".json": "json",
        ".yaml": "yaml",
        ".yml": "yaml",
        ".toml": "toml",
        ".sql": "sql",
        ".sh": "bash",
    }

    def detect_language(self, file_path: Path) -> str:
        return self.LANGUAGE_MAP.get(file_path.suffix.lower(), "text")

    def chunk_file(
        self,
        file_path: Path,
        repository_path: Path,
        repository_id: int,
    ) -> list[CodeChunk]:

        content = file_path.read_text(
            encoding="utf-8",
            errors="ignore",
        )

        lines = content.splitlines()

        chunks = []
        step = self.CHUNK_SIZE - self.CHUNK_OVERLAP

        for index, start in enumerate(range(0, len(lines), step)):

            end = start + self.CHUNK_SIZE
            chunk_lines = lines[start:end]

            if not chunk_lines:
                continue

            chunks.append(
                CodeChunk(
                    repository_id=repository_id,
                    file_path=str(
                        file_path.relative_to(repository_path)
                    ),
                    content="\n".join(chunk_lines),
                    chunk_index=index,
                    start_line=start + 1,
                    end_line=min(end, len(lines)),
                    language=self.detect_language(file_path),
                )
            )

        return chunks