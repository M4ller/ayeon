"""Cognition engine boundary for Ayeon Core."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from ayeon.contracts.cognition import CognitiveOutput
from ayeon.contracts.cognitive_context import CognitiveContext


@runtime_checkable
class CognitionEngine(Protocol):
    """Structural boundary for Ayeon's cognition implementations.

    A cognition engine receives immutable cognitive context and produces
    structured cognitive output. This boundary exposes no operational tools,
    authorization capability, or mutable domain ownership.
    """

    def process(
        self,
        context: CognitiveContext,
    ) -> CognitiveOutput:
        """Process one cognitive context into structured output."""
        ...