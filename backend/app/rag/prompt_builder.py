from __future__ import annotations

from backend.app.config import settings
from backend.app.rag.retriever import RetrievedChunk


SYSTEM_PROMPT = """
You are ShopMind, an e-commerce customer support assistant.

You must follow these rules:
1. Answer only using the provided context.
2. If the context is not enough, say you do not have enough verified information.
3. Do not invent policies, prices, warranty terms, shipping times, or order status.
4. Be concise, helpful, and professional.
5. If multiple sources are relevant, synthesize them carefully.
6. Do not write source citations in the answer. Sources will be attached separately by the system.
""".strip()


class PromptBuilder:
    def _build_context(self, chunks: list[RetrievedChunk]) -> str:
        blocks: list[str] = []
        total_chars = 0

        for index, chunk in enumerate(chunks, start=1):
            header = (
                f"[Source {index}]\n"
                f"Score: {chunk.score:.4f}\n"
                f"Document type: {chunk.document_type}\n"
                f"Category: {chunk.category}\n"
                f"Source: {chunk.source}\n"
                f"Title: {chunk.title}\n"
                "Content:\n"
            )
            separator_length = 2 if blocks else 0
            remaining = (
                settings.max_context_chars
                - total_chars
                - separator_length
                - len(header)
            )
            if remaining <= 0:
                break

            content = chunk.text[:remaining]
            block = f"{header}{content}"
            blocks.append(block)
            total_chars += separator_length + len(block)

            if len(content) < len(chunk.text):
                break

        return "\n\n".join(blocks)

    def build_messages(
        self,
        query: str,
        chunks: list[RetrievedChunk],
    ) -> list[dict[str, str]]:
        context = self._build_context(chunks)
        user_prompt = (
            f"Context:\n{context}\n\n"
            f"Customer question:\n{query}\n\n"
            "Write the answer:"
        )
        return [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]
