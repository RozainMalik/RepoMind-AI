import ollama
from app.core.config import settings


class LLMService:

    def __init__(self):
        self.model = settings.LLM_MODEL


    def generate(self, prompt: str):

        response = ollama.chat(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": 
                    """
                    You are RepoMind AI, an expert software engineer.
                    You understand large codebases and explain code clearly.
                    """
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )


        return response["message"]["content"]