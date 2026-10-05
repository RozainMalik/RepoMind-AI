import ollama

from app.core.config import settings


class LLMService:

    SYSTEM_PROMPT = (
        "You are a careful assistant that answers questions about source code. "
        "Base every answer strictly on the code excerpts you are given."
    )

    def __init__(self):
        self.model = settings.LLM_MODEL

    def generate(self, prompt: str) -> str:
        try:
            response = ollama.chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                options={
                    # Low randomness: fewer invented file names and details
                    "temperature": 0.1,
                    # Room for 5 chunks of ~100 lines plus rules and answer.
                    # Without this Ollama may silently truncate the prompt.
                    "num_ctx": 8192,
                },
            )
        except Exception as e:
            raise RuntimeError(
                f"Could not reach the Ollama model '{self.model}'. "
                f"Is Ollama running, and has the model been pulled? ({e})"
            ) from e

        return response["message"]["content"]