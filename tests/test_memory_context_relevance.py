"""Tests for memory relevance coordination."""

from ayeon.contracts.common import new_memory_record_id
from ayeon.contracts.memory_context_eligibility import (
    MemoryContextEligibilityDecision,
    MemoryContextEligibilityOutcome,
)
from ayeon.contracts.memory_context_relevance import (
    MemoryContextRelevanceOutcome,
)
from ayeon.memory.context_relevance import MemoryContextRelevanceCoordinator


def test_ineligible_memory_never_reaches_relevance_evaluator() -> None:
    eligibility = MemoryContextEligibilityDecision(
        memory_record_id=new_memory_record_id(),
        outcome=MemoryContextEligibilityOutcome.INELIGIBLE,
        reason="Verification failed.",
    )

    class MustNotBeCalled:
        def evaluate(self, user_input, decoded):
            raise AssertionError("Ineligible memory reached evaluator")

    decision = MemoryContextRelevanceCoordinator().evaluate(
        user_input="¿Qué recuerdas?",
        eligibility=eligibility,
        decoded=None,
        evaluator=MustNotBeCalled(),
    )

    assert decision.outcome is MemoryContextRelevanceOutcome.INELIGIBLE
    assert decision.memory_record_id == eligibility.memory_record_id

def test_eligible_memory_reaches_relevance_evaluator() -> None:
    from test_sqlite_memory_repository import make_record

    from ayeon.memory.decoder import decode_memory_record
    from ayeon.memory.serialization import encode_memory_record

    record = make_record()
    decoded = decode_memory_record(encode_memory_record(record))
    eligibility = MemoryContextEligibilityDecision(
        memory_record_id=record.memory_record_id,
        outcome=MemoryContextEligibilityOutcome.ELIGIBLE,
        reason="Evidence matched.",
    )
    calls = []

    class RelevantEvaluator:
        def evaluate(self, user_input, memory):
            calls.append((user_input, memory))
            return MemoryContextRelevanceOutcome.RELEVANT

    decision = MemoryContextRelevanceCoordinator().evaluate(
        user_input="Recuerda este dato",
        eligibility=eligibility,
        decoded=decoded,
        evaluator=RelevantEvaluator(),
    )

    assert calls == [("Recuerda este dato", decoded)]
    assert decision.outcome is MemoryContextRelevanceOutcome.RELEVANT


def test_mismatched_decoded_identity_never_reaches_evaluator() -> None:
    import pytest
    from test_sqlite_memory_repository import make_record

    from ayeon.memory.decoder import decode_memory_record
    from ayeon.memory.serialization import encode_memory_record

    decoded = decode_memory_record(encode_memory_record(make_record()))
    eligibility = MemoryContextEligibilityDecision(
        memory_record_id=new_memory_record_id(),
        outcome=MemoryContextEligibilityOutcome.ELIGIBLE,
        reason="Evidence matched.",
    )

    class MustNotBeCalled:
        def evaluate(self, user_input, memory):
            raise AssertionError("Mismatched memory reached evaluator")

    with pytest.raises(ValueError, match="memory_record_id"):
        MemoryContextRelevanceCoordinator().evaluate(
            user_input="Recuerda este dato",
            eligibility=eligibility,
            decoded=decoded,
            evaluator=MustNotBeCalled(),
        )

def test_invalid_evaluator_result_becomes_unknown() -> None:
    from test_sqlite_memory_repository import make_record

    from ayeon.memory.decoder import decode_memory_record
    from ayeon.memory.serialization import encode_memory_record

    record = make_record()
    decoded = decode_memory_record(encode_memory_record(record))
    eligibility = MemoryContextEligibilityDecision(
        memory_record_id=record.memory_record_id,
        outcome=MemoryContextEligibilityOutcome.ELIGIBLE,
        reason="Evidence matched.",
    )

    class InvalidEvaluator:
        def evaluate(self, user_input, memory):
            return "relevant"

    decision = MemoryContextRelevanceCoordinator().evaluate(
        user_input="Recuerda este dato",
        eligibility=eligibility,
        decoded=decoded,
        evaluator=InvalidEvaluator(),
    )

    assert decision.outcome is MemoryContextRelevanceOutcome.UNKNOWN
