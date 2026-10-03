from pydantic import BaseModel


class CodeChunk(BaseModel):
    repository_id: int
    file_path: str
    content: str
    chunk_index: int
    start_line: int
    end_line: int
    language: str