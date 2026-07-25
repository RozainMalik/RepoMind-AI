class PromptService:

    def build_prompt(
        self,
        question: str,
        chunks
    ):

        context = ""

        for i, chunk in enumerate(chunks):

            context += f"""
--------------------
Chunk {i+1}

File:
{chunk.payload["file_path"]}

Code:
{chunk.payload["content"]}

"""

        prompt = f"""
You are RepoMind AI, an assistant that understands software repositories.

Answer the user's question using ONLY the provided repository context.

If the answer cannot be found in the context, say:
"I could not find this information in the repository."

Context:
{context}

Question:
{question}


Answer:
"""

        return prompt