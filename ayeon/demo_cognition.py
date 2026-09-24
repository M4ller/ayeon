"""Deterministic text responses for the Ayeon console demo."""

from __future__ import annotations

from ayeon.contracts.cognition import CognitiveOutput
from ayeon.contracts.cognitive_context import CognitiveContext


class DemoCognitionEngine:
    """Demo responses without a language model or tool access."""

    def process(self, context: CognitiveContext) -> CognitiveOutput:
        message = context.user_input.strip().casefold()

        if message in {"hola", "hola ayeon"}:
            response = "Hola. Soy la demo de texto de Ayeon."
        elif message in {"ayuda", "qué puedes hacer", "que puedes hacer"}:
            response = (
                "Por ahora puedo mostrar respuestas de prueba. "
                "La memoria se prueba con python -m ayeon.demo_memory."
            )
        else:
            response = (
                "Te leí. Todavía no tengo un modelo conversacional "
                "para responder libremente."
            )

        return CognitiveOutput(
            trace=context.trace,
            spoken_response=response,
        )
