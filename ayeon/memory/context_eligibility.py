"""Conservative eligibility policy for a known original memory record."""

from __future__ import annotations

from ayeon.contracts.memory import MemoryRecord
from ayeon.contracts.memory_context_eligibility import (
    MemoryContextEligibilityDecision,
    MemoryContextEligibilityOutcome,
)
from ayeon.contracts.memory_persistence_verification import (
    MemoryPersistenceVerificationResult,
)
from ayeon.contracts.memory_retrieval_decoding import MemoryDecodeOutcome
from ayeon.contracts.memory_retrieval_verification import (
    MemoryRetrievalVerificationResult,
)
from ayeon.contracts.verification import VerificationState
from ayeon.memory.serialization import encode_memory_record


class MemoryContextEligibilityPolicy:
    """Assess evidence without adding memory to cognitive context."""

    def evaluate(
        self,
        *,
        record: MemoryRecord,
        retrieval_verification: MemoryRetrievalVerificationResult,
        persistence_verification: MemoryPersistenceVerificationResult,
    ) -> MemoryContextEligibilityDecision:
        decoding = retrieval_verification.decoding
        decoded = decoding.decoded

        eligible = (
            retrieval_verification.state is VerificationState.VERIFIED
            and persistence_verification.state is VerificationState.VERIFIED
            and retrieval_verification.memory_record_id == record.memory_record_id
            and persistence_verification.memory_record_id == record.memory_record_id
            and (
                persistence_verification.trace.correlation_id
                == record.trace.correlation_id
            )
            and decoding.outcome is MemoryDecodeOutcome.DECODED
            and decoded is not None
            and decoded.memory_record_id == record.memory_record_id
            and decoded.correlation_id == record.trace.correlation_id
            and decoding.retrieval.payload == encode_memory_record(record)
        )

        return MemoryContextEligibilityDecision(
            memory_record_id=record.memory_record_id,
            outcome=(
                MemoryContextEligibilityOutcome.ELIGIBLE
                if eligible
                else MemoryContextEligibilityOutcome.INELIGIBLE
            ),
            reason=(
                "Known original and independently checked bytes agree."
                if eligible
                else "Required memory evidence does not agree."
            ),
        )
