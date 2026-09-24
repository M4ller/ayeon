"""Gemini text generator for Ayeon's cognition engine."""

from __future__ import annotations

import os

AYEON_INSTRUCTIONS = (
    "Eres Ayeon, asistente virtual de Felipe. Responde en español de Chile, "
    "con cercanía, claridad y brevedad. No afirmes recordar información que "
    "no recibiste ni haber ejecutado acciones. Si no sabes algo, dilo."
)


class GeminiGenerator:
    """Generate text without granting the model tools or actions."""

    def __init__(self, *, client=None, model: str | None = None) -> None:
        self._client = client
        self._model = model or os.getenv(
            "AYEON_GEMINI_MODEL", "gemini-3.5-flash-lite"
        )
        if not self._model.strip():
            raise ValueError("model must not be blank")

    def generate(self, prompt: str) -> str:
        if not prompt.strip():
            raise ValueError("prompt must not be blank")

        from google import genai
        from google.genai import types

        if self._client is None:
            self._client = genai.Client()

        response = self._client.models.generate_content(
            model=self._model,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=AYEON_INSTRUCTIONS,
                automatic_function_calling=types.AutomaticFunctionCallingConfig(
                    disable=True
                ),
            ),
        )
        text = response.text
        if not isinstance(text, str) or not text.strip():
            raise ValueError("Gemini response did not contain text")
        return text.strip()
