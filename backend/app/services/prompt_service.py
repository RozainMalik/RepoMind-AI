class PromptService:

    def build_prompt(
        self,
        question: str,
        chunks,
    ):
        context_blocks = []

        for i, chunk in enumerate(chunks, start=1):
            payload = chunk.payload

            context_blocks.append(
                f"""[Chunk {i}]
File: {payload["file_path"]}
Lines: {payload["start_line"]}-{payload["end_line"]}

{payload["content"]}"""
            )

        context = "\n\n--------------------\n\n".join(context_blocks)

        prompt = f"""You answer questions about a source code repository.

You are given code excerpts retrieved from the repository. They are only a small part of it.

Rules:
- Use ONLY the excerpts below. Do not use outside knowledge about the project.
- Mention only file paths that appear in the excerpts, exactly as written.
- When you point to code, give the file path and line range.
- If the excerpts answer only part of the question, answer that part and say what is missing.
- If the excerpts do not contain the answer, reply exactly: "I could not find this information in the retrieved code."
- Be concise. Do not repeat the question.

Repository excerpts:

{context}

Question: {question}

Answer:"""

        return prompt