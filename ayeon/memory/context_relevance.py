"""Coordinate eligibility and relevance without building context."""

from __future__ import annotations

from typing import Protocol

from ayeon.contracts.memory_context_eligibility import (
    MemoryContextEligibilityDecision,
    MemoryContextEligibilityOutcome,
)
from ayeon.contracts.memory_context_relevance import (
    MemoryContextRelevanceDecision,
    MemoryContextRelevanceOutcome,
)
from ayeon.contracts.memory_decoding import DecodedMemoryRecord


class MemoryRelevanceEvaluator(Protocol):
    def evaluate(
        self,
        user_input: str,
        decoded: DecodedMemoryRecord,
    ) -> MemoryContextRelevanceOutcome: ...


class MemoryContextRelevanceCoordinator:
    """Only eligible, identity-matched memory reaches an evaluator."""

    def evaluate(
        self,
        *,
        user_input: str,
        eligibility: MemoryContextEligibilityDecision,
        decoded: DecodedMemoryRecord | None,
        evaluator: MemoryRelevanceEvaluator,
    ) -> MemoryContextRelevanceDecision:
        if not user_input.strip():
            raise ValueError("user_input must not be blank")

        record_id = eligibility.memory_record_id

        if eligibility.outcome is MemoryContextEligibilityOutcome.INELIGIBLE:
            return MemoryContextRelevanceDecision(
                memory_record_id=record_id,
                outcome=MemoryContextRelevanceOutcome.INELIGIBLE,
                reason="Memory did not pass evidence eligibility.",
            )

        if decoded is None:
            return MemoryContextRelevanceDecision(
                memory_record_id=record_id,
                outcome=MemoryContextRelevanceOutcome.UNKNOWN,
                reason="Eligible memory has no decoded content.",
            )

        if decoded.memory_record_id != record_id:
            raise ValueError("decoded memory_record_id must match eligibility")

        try:
            outcome = evaluator.evaluate(user_input, decoded)
        except Exception as exc:
            return MemoryContextRelevanceDecision(
                memory_record_id=record_id,
                outcome=MemoryContextRelevanceOutcome.UNKNOWN,
                reason=f"Relevance evaluation failed: {type(exc).__name__}.",
            )

        if (
            not isinstance(outcome, MemoryContextRelevanceOutcome)
            or outcome is MemoryContextRelevanceOutcome.INELIGIBLE
        ):
            outcome = MemoryContextRelevanceOutcome.UNKNOWN

        return MemoryContextRelevanceDecision(
            memory_record_id=record_id,
            outcome=outcome,
            reason="Relevance evaluator returned a decision.",
        )
