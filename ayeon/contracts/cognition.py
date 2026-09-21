"""Cognition output contracts for Ayeon Core."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType

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

        safe_memory_intents = tuple(
            MappingProxyType(dict(intent))
            for intent in self.memory_intents
        )
        safe_emotional_update = MappingProxyType(
            dict(self.emotional_update)
        )
        safe_attention_update = MappingProxyType(
            dict(self.attention_update)
        )
        safe_avatar_state = MappingProxyType(
            dict(self.avatar_state)
        )

        object.__setattr__(
            self,
            "memory_intents",
            safe_memory_intents,
        )
        object.__setattr__(
            self,
            "emotional_update",
            safe_emotional_update,
        )
        object.__setattr__(
            self,
            "attention_update",
            safe_attention_update,
        )
        object.__setattr__(
            self,
            "avatar_state",
            safe_avatar_state,
        )
