"""Cognition coordination for Ayeon Core."""

from __future__ import annotations

from ayeon.contracts.cognition import CognitiveOutput
from ayeon.contracts.common import TraceContext
from ayeon.contracts.state import AyeonStateSnapshot
from ayeon.core.cognition.engine import CognitionEngine
from ayeon.core.context.builder import ContextBuilder


class CognitionCoordinator:
    """Coordinate context construction and cognitive processing.

    The coordinator builds immutable cognitive context and delegates
    reasoning to a cognition engine. It performs no authorization,
    tool execution, or mutable domain-state ownership.
    """

    def __init__(
        self,
        *,
        context_builder: ContextBuilder,
        cognition_engine: CognitionEngine,
    ) -> None:
        self._context_builder = context_builder
        self._cognition_engine = cognition_engine

    def process(
        self,
        *,
        trace: TraceContext,
        user_input: str,
        state_snapshot: AyeonStateSnapshot,
    ) -> CognitiveOutput:
        """Build context and produce one cognitive output."""

        context = self._context_builder.build(
            trace=trace,
            user_input=user_input,
            state_snapshot=state_snapshot,
        )

        return self._cognition_engine.process(context)
