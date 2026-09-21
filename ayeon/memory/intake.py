"""Deterministic memory admission policy for Ayeon Core."""

from __future__ import annotations

from ayeon.contracts.memory import (
    MemoryAdmissionDecision,
    MemoryAdmissionOutcome,
    MemoryIntent,
)

MEMORY_INTAKE_POLICY_SOURCE = "memory_intake_policy"


class MemoryIntakePolicy:
    """Evaluate memory intents without creating or persisting memories."""

    def __init__(
        self,
        *,
        default_outcome: MemoryAdmissionOutcome,
    ) -> None:
        if not isinstance(default_outcome, MemoryAdmissionOutcome):
            raise TypeError(
                "default_outcome must be MemoryAdmissionOutcome"
            )

        self._default_outcome = default_outcome

    def evaluate(
        self,
        intent: MemoryIntent,
    ) -> MemoryAdmissionDecision:
        """Return the configured deterministic admission decision."""

        if not isinstance(intent, MemoryIntent):
            raise TypeError("intent must be MemoryIntent")

        return MemoryAdmissionDecision(
            memory_intent_id=intent.memory_intent_id,
            outcome=self._default_outcome,
            decided_by=MEMORY_INTAKE_POLICY_SOURCE,
            trace=intent.trace,
            reason="Configured memory admission policy outcome.",
        )
