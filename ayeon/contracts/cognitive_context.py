"""Cognitive context contracts for Ayeon Core."""

from __future__ import annotations

from dataclasses import dataclass

from ayeon.contracts.common import TraceContext
from ayeon.contracts.state import AyeonStateSnapshot


@dataclass(frozen=True, slots=True)
class CognitiveContext:
    """Immutable input context presented to Ayeon's cognition layer.

    Cognition receives a coherent state snapshot rather than mutable
    domain ownership or direct operational capabilities.
    """

    trace: TraceContext
    user_input: str
    state_snapshot: AyeonStateSnapshot

    def __post_init__(self) -> None:
        if not self.user_input.strip():
            raise ValueError("user_input must not be blank")