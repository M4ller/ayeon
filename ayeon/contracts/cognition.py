"""Cognition output contracts for Ayeon Core."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

from ayeon.contracts.actions import ActionIntent
from ayeon.contracts.common import TraceContext


@dataclass(frozen=True, slots=True)
class CognitiveOutput:
    """Structured result produced by Ayeon's cognition layer.

    Cognition may propose actions and internal updates, but this contract
    grants no authorization and exposes no execution capability.
    """

    trace: TraceContext
    spoken_response: str | None = None
    action_intents: tuple[ActionIntent, ...] = ()
    memory_intents: tuple[Mapping[str, object], ...] = ()
    emotional_update: Mapping[str, object] = field(default_factory=dict)
    attention_update: Mapping[str, object] = field(default_factory=dict)
    executive_signals: tuple[str, ...] = ()
    avatar_state: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.spoken_response is not None and not self.spoken_response.strip():
            raise ValueError("spoken_response must not be blank")

        for intent in self.action_intents:
            if intent.trace.correlation_id != self.trace.correlation_id:
                raise ValueError(
                    "action intent must share CognitiveOutput correlation_id"
                )
