from app.services.retrieval_service import RetrievalService
from app.services.prompt_service import PromptService
from app.services.llm_service import LLMService
from pathlib import Path

class ChatService:

    def __init__(self):
        self.retriever = RetrievalService()
        self.prompt = PromptService()
        self.llm = LLMService()

    def ask(self, question: str, repository_id: int):
        chunks = self.retriever.retrieve(
            question,
            repository_id,
            limit=5
        )
        prompt = self.prompt.build_prompt(
            question,
            chunks
        )
        answer = self.llm.generate(prompt)
        
        sources = []
        for chunk in chunks:
            sources.append(
                {
                    "file_path": chunk.payload["file_path"],
                    "start_line": chunk.payload["start_line"],
                    "end_line": chunk.payload["end_line"],
                    "score": chunk.score
                }
            )

        return {
            "answer": answer,
            "sources": sources
        }