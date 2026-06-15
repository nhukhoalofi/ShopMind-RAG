from __future__ import annotations

from groq import Groq

from backend.app.config import settings


class GroqGenerator:
    def __init__(self) -> None:
        if not settings.groq_api_key:
            raise RuntimeError(
                "GROQ_API_KEY is missing. Add it to the project .env file."
            )
        self.client = Groq(api_key=settings.groq_api_key)

    def generate(self, messages: list[dict[str, str]]) -> str:
        response = self.client.chat.completions.create(
            model=settings.groq_model,
            messages=messages,
            temperature=settings.llm_temperature,
            max_tokens=settings.llm_max_tokens,
        )
        content = response.choices[0].message.content
        if not content or not content.strip():
            raise RuntimeError("Groq returned an empty answer.")
        return content.strip()
