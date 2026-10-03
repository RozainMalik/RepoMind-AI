from pydantic import BaseModel


class Source(BaseModel):
    file_path: str
    start_line: int
    end_line: int
    score: float


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source]