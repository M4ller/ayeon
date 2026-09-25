"""Text generation adapter for Ayeon's cognition boundary."""

from __future__ import annotations

from typing import Protocol

from ayeon.contracts.cognition import CognitiveOutput
from ayeon.contracts.cognitive_context import CognitiveContext


class TextGenerator(Protocol):
    """Generate text without access to actions or domain state."""

    def generate(self, prompt: str) -> str: ...


class TextCognitionEngine:
    """Turn generated text into a structured cognitive response."""

    def __init__(self, generator: TextGenerator) -> None:
        self._generator = generator

    def process(self, context: CognitiveContext) -> CognitiveOutput:
        prompt = self._build_prompt(context)
        response = self._generator.generate(prompt)

        if not isinstance(response, str) or not response.strip():
            raise ValueError("text generator must return non-blank text")

        return CognitiveOutput(
            trace=context.trace,
            spoken_response=response.strip(),
        )

    def _build_prompt(self, context: CognitiveContext) -> str:
        if not context.memories:
            return context.user_input

        memory_lines = []

        for entry in context.memories:
            memory_lines.append(
                f"- {dict(entry.decoded.content)}"
            )

        memories = "\n".join(memory_lines)

        return (
            "Relevant verified memories:\n"
            f"{memories}\n\n"
            "User request:\n"
            f"{context.user_input}"
        )