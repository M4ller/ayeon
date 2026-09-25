"""Cognitive context construction for Ayeon Core."""

from __future__ import annotations

from ayeon.contracts.cognitive_context import CognitiveContext
from ayeon.contracts.common import TraceContext
from ayeon.contracts.memory_context_entry import MemoryContextEntry
from ayeon.contracts.state import AyeonStateSnapshot


class ContextBuilder:
    """Build immutable context for Ayeon's cognition layer.

    The builder assembles already-authoritative read-only state into a
    CognitiveContext. It owns no domain state and performs no mutation.
    """

    def build(
        self,
        *,
        trace: TraceContext,
        user_input: str,
        state_snapshot: AyeonStateSnapshot,
        memories: tuple[MemoryContextEntry, ...] = (),
    ) -> CognitiveContext:
        """Build one cognitive context from the current input and snapshot."""

        return CognitiveContext(
            trace=trace,
            user_input=user_input,
            state_snapshot=state_snapshot,
            memories=memories,
        )