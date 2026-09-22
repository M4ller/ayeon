"""Deterministic coordination for memory persistence verification."""

from __future__ import annotations

from ayeon.contracts.memory import MemoryRecord
from ayeon.contracts.memory_persistence import MemoryPersistenceResult
from ayeon.contracts.memory_persistence_result_verification import (
    MemoryPersistenceResultVerification,
)
from ayeon.contracts.memory_persistence_verification import (
    MemoryPersistenceVerificationResult,
)
from ayeon.contracts.verification import VerificationState
from ayeon.memory.persistence_verifier import MemoryPersistenceVerifier


class MemoryPersistenceVerificationCoordinator:
    """Coordinate verification and validate verifier result provenance."""

    def verify(
        self,
        record: MemoryRecord,
        persistence: MemoryPersistenceResult,
        verifier: MemoryPersistenceVerifier,
    ) -> MemoryPersistenceResultVerification:
        """Verify persistence and return its validated association."""

        if persistence.memory_record_id != record.memory_record_id:
            raise ValueError(
                "inconsistent persistence result: memory_record_id"
            )

        if (
            persistence.trace.correlation_id
            != record.trace.correlation_id
        ):
            raise ValueError(
                "inconsistent persistence result: correlation_id"
            )

        try:
            verification = verifier.verify(record, persistence)
        except Exception as exc:
            verification = MemoryPersistenceVerificationResult(
                memory_record_id=record.memory_record_id,
                repository_name=persistence.repository_name,
                state=VerificationState.UNKNOWN,
                verified_by=verifier.name,
                trace=record.trace,
                reason=(
                    "Memory persistence verifier raised an exception; "
                    "durable verification is unknown: "
                    f"{type(exc).__name__}"
                ),
            )

        if not isinstance(
            verification,
            MemoryPersistenceVerificationResult,
        ):
            raise TypeError(
                "verifier result must be "
                "MemoryPersistenceVerificationResult"
            )

        if verification.verified_by != verifier.name:
            raise ValueError(
                "verification verified_by must match selected verifier"
            )

        return MemoryPersistenceResultVerification(
            persistence=persistence,
            verification=verification,
        )