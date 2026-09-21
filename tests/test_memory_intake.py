import pytest

from ayeon.contracts.common import TraceContext
from ayeon.contracts.memory import (
    MemoryAdmissionOutcome,
    MemoryIntent,
)
from ayeon.memory.intake import MemoryIntakePolicy


@pytest.mark.parametrize(
    "outcome",
    [
        MemoryAdmissionOutcome.ACCEPT,
        MemoryAdmissionOutcome.REJECT,
        MemoryAdmissionOutcome.DEFER,
    ],
)
def test_memory_intake_preserves_intent_identity_and_trace(
    outcome: MemoryAdmissionOutcome,
) -> None:
    trace = TraceContext.root()
    intent = MemoryIntent(
        content={"kind": "observation"},
        proposed_by="cognition",
        trace=trace,
    )
    policy = MemoryIntakePolicy(default_outcome=outcome)

    decision = policy.evaluate(intent)

    assert decision.memory_intent_id == intent.memory_intent_id
    assert decision.trace is trace
    assert decision.outcome is outcome


def test_memory_intake_rejects_invalid_default_outcome() -> None:
    with pytest.raises(
        TypeError,
        match="default_outcome must be MemoryAdmissionOutcome",
    ):
        MemoryIntakePolicy(default_outcome="accept")


def test_memory_intake_rejects_non_memory_intent() -> None:
    policy = MemoryIntakePolicy(
        default_outcome=MemoryAdmissionOutcome.DEFER,
    )

    with pytest.raises(TypeError, match="intent must be MemoryIntent"):
        policy.evaluate({"kind": "observation"})
