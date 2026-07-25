from app.services.retrieval_service import RetrievalService
from app.services.prompt_service import PromptService
from app.services.llm_service import LLMService

class ChatService:

    def __init__(self):
        self.retriever = RetrievalService()
        self.prompt = PromptService()
        self.llm = LLMService()

    def ask(self, question: str):
        chunks = self.retriever.retrieve(
            question,
            limit=5
        )
        prompt = self.prompt.build_prompt(
            question,
            chunks
        )
        answer = self.llm.generate(prompt)

        return answer