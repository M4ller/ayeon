from datetime import datetime

import pytest

from ayeon.contracts.common import TraceContext
from ayeon.contracts.memory import (
    MemoryAdmissionDecision,
    MemoryAdmissionOutcome,
    MemoryIntent,
)


def make_intent(trace: TraceContext) -> MemoryIntent:
    return MemoryIntent(
        content={"kind": "observation"},
        proposed_by="cognition",
        trace=trace,
    )


def test_memory_admission_decision_preserves_intent_identity() -> None:
    trace = TraceContext.root()
    intent = make_intent(trace)

    decision = MemoryAdmissionDecision(
        memory_intent_id=intent.memory_intent_id,
        outcome=MemoryAdmissionOutcome.ACCEPT,
        decided_by="memory_intake",
        trace=trace,
        reason="proposal satisfies admission policy",
    )

    assert decision.memory_intent_id == intent.memory_intent_id
    assert decision.outcome is MemoryAdmissionOutcome.ACCEPT


def test_memory_admission_decision_rejects_empty_decided_by() -> None:
    trace = TraceContext.root()
    intent = make_intent(trace)

    with pytest.raises(ValueError, match="decided_by must not be empty"):
        MemoryAdmissionDecision(
            memory_intent_id=intent.memory_intent_id,
            outcome=MemoryAdmissionOutcome.REJECT,
            decided_by=" ",
            trace=trace,
            reason="proposal rejected",
        )


def test_memory_admission_decision_rejects_empty_reason() -> None:
    trace = TraceContext.root()
    intent = make_intent(trace)

    with pytest.raises(ValueError, match="reason must not be empty"):
        MemoryAdmissionDecision(
            memory_intent_id=intent.memory_intent_id,
            outcome=MemoryAdmissionOutcome.DEFER,
            decided_by="memory_intake",
            trace=trace,
            reason=" ",
        )


def test_memory_admission_decision_rejects_naive_timestamp() -> None:
    trace = TraceContext.root()
    intent = make_intent(trace)

    with pytest.raises(ValueError, match="decided_at must be timezone-aware"):
        MemoryAdmissionDecision(
            memory_intent_id=intent.memory_intent_id,
            outcome=MemoryAdmissionOutcome.ACCEPT,
            decided_by="memory_intake",
            trace=trace,
            reason="proposal satisfies admission policy",
            decided_at=datetime(2026, 1, 1),
        )


def test_memory_admission_decision_rejects_invalid_outcome_type() -> None:
    trace = TraceContext.root()
    intent = make_intent(trace)

    with pytest.raises(
        TypeError,
        match="outcome must be MemoryAdmissionOutcome",
    ):
        MemoryAdmissionDecision(
            memory_intent_id=intent.memory_intent_id,
            outcome="accept",
            decided_by="memory_intake",
            trace=trace,
            reason="proposal satisfies admission policy",
        )
