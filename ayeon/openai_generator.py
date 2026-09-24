"""OpenAI Responses text generator for Ayeon's cognition engine."""

from __future__ import annotations

import os

AYEON_INSTRUCTIONS = (
    "Eres Ayeon, asistente virtual de Felipe. Responde en español de Chile, "
    "con cercanía, claridad y brevedad. No afirmes recordar información que "
    "no recibiste ni haber ejecutado acciones. Si no sabes algo, dilo."
)


class OpenAIResponsesGenerator:
    """Generate text without exposing tools or action capabilities."""

    def __init__(
        self,
        *,
        client=None,
        model: str | None = None,
    ) -> None:
        self._client = client
        self._model = model or os.getenv("AYEON_OPENAI_MODEL", "gpt-6-astra")
        if not self._model.strip():
            raise ValueError("model must not be blank")

    def generate(self, prompt: str) -> str:
        if not prompt.strip():
            raise ValueError("prompt must not be blank")

        if self._client is None:
            from openai import OpenAI

            self._client = OpenAI()

        response = self._client.responses.create(
            model=self._model,
            instructions=AYEON_INSTRUCTIONS,
            input=prompt,
            store=False,
            max_output_tokens=1024,
        )
        text = response.output_text
        if not isinstance(text, str) or not text.strip():
            raise ValueError("OpenAI response did not contain text")
        return text.strip()
