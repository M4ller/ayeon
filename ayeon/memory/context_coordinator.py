"""Coordinate verified memory selection for cognitive context."""

from __future__ import annotations

from ayeon.contracts.memory import MemoryRecord
from ayeon.contracts.memory_context_entry import MemoryContextEntry
from ayeon.contracts.memory_persistence_verification import (
    MemoryPersistenceVerificationResult,
)
from ayeon.contracts.memory_retrieval_verification import (
    MemoryRetrievalVerificationResult,
)
from ayeon.memory.context_eligibility import MemoryContextEligibilityPolicy
from ayeon.memory.context_inclusion import MemoryContextInclusionPolicy
from ayeon.memory.context_relevance import (
    MemoryContextRelevanceCoordinator,
    MemoryRelevanceEvaluator,
)


class MemoryContextCoordinator:
    """Coordinate verified memory from evidence to context inclusion."""

    def select(
        self,
        *,
        user_input: str,
        record: MemoryRecord,
        retrieval_verification: MemoryRetrievalVerificationResult,
        persistence_verification: MemoryPersistenceVerificationResult,
        evaluator: MemoryRelevanceEvaluator,
    ) -> MemoryContextEntry | None:
        eligibility = MemoryContextEligibilityPolicy().evaluate(
            record=record,
            retrieval_verification=retrieval_verification,
            persistence_verification=persistence_verification,
        )

        decoded = retrieval_verification.decoding.decoded

        relevance = MemoryContextRelevanceCoordinator().evaluate(
            user_input=user_input,
            eligibility=eligibility,
            decoded=decoded,
            evaluator=evaluator,
        )

        return MemoryContextInclusionPolicy().include(
            relevance=relevance,
            decoded=decoded,
        )