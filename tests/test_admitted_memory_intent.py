import pytest

from ayeon.contracts.common import TraceContext
from ayeon.contracts.memory import (
    AdmittedMemoryIntent,
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


def make_decision(
    intent: MemoryIntent,
    *,
    outcome: MemoryAdmissionOutcome = MemoryAdmissionOutcome.ACCEPT,
    trace: TraceContext | None = None,
) -> MemoryAdmissionDecision:
    return MemoryAdmissionDecision(
        memory_intent_id=intent.memory_intent_id,
        outcome=outcome,
        decided_by="memory_intake_policy",
        trace=trace or intent.trace,
        reason="test admission decision",
    )


def test_admitted_memory_intent_preserves_intent_and_decision() -> None:
    trace = TraceContext.root()
    intent = make_intent(trace)
    decision = make_decision(intent)

    admitted = AdmittedMemoryIntent(
        intent=intent,
        admission=decision,
    )

    assert admitted.intent is intent
    assert admitted.admission is decision


def test_admitted_memory_intent_requires_accept() -> None:
    trace = TraceContext.root()
    intent = make_intent(trace)
    decision = make_decision(
        intent,
        outcome=MemoryAdmissionOutcome.REJECT,
    )

    with pytest.raises(
        ValueError,
        match="admission outcome must be ACCEPT",
    ):
        AdmittedMemoryIntent(
            intent=intent,
            admission=decision,
        )


def test_admitted_memory_intent_requires_matching_intent_id() -> None:
    trace = TraceContext.root()
    intent = make_intent(trace)
    other_intent = make_intent(trace)
    decision = make_decision(other_intent)

    with pytest.raises(
        ValueError,
        match="admission memory_intent_id must match intent memory_intent_id",
    ):
        AdmittedMemoryIntent(
            intent=intent,
            admission=decision,
        )


def test_admitted_memory_intent_requires_matching_correlation() -> None:
    intent = make_intent(TraceContext.root())
    decision = make_decision(
        intent,
        trace=TraceContext.root(),
    )

    with pytest.raises(
        ValueError,
        match="admission correlation must match intent correlation",
    ):
        AdmittedMemoryIntent(
            intent=intent,
            admission=decision,
        )


def test_admitted_memory_intent_rejects_invalid_intent_type() -> None:
    trace = TraceContext.root()
    valid_intent = make_intent(trace)
    decision = make_decision(valid_intent)

    with pytest.raises(TypeError, match="intent must be MemoryIntent"):
        AdmittedMemoryIntent(
            intent={"kind": "observation"},
            admission=decision,
        )


def test_admitted_memory_intent_rejects_invalid_admission_type() -> None:
    intent = make_intent(TraceContext.root())

    with pytest.raises(
        TypeError,
        match="admission must be MemoryAdmissionDecision",
    ):
        AdmittedMemoryIntent(
            intent=intent,
            admission={"outcome": "accept"},
        )
