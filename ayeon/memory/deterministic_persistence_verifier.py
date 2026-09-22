"""Deterministic durable memory persistence verification."""

from __future__ import annotations

from ayeon.contracts.memory import MemoryRecord
from ayeon.contracts.memory_persistence import MemoryPersistenceResult
from ayeon.contracts.memory_persistence_verification import (
    MemoryPersistenceVerificationResult,
)
from ayeon.contracts.verification import VerificationState
from ayeon.memory.durable_evidence import DurableMemoryEvidenceReader
from ayeon.memory.serialization import encode_memory_record


class DeterministicMemoryPersistenceVerifier:
    """Verify canonical durable evidence against an expected memory record."""

    def __init__(
        self,
        evidence_reader: DurableMemoryEvidenceReader,
    ) -> None:
        self._evidence_reader = evidence_reader

    @property
    def name(self) -> str:
        return "deterministic_memory_persistence_verifier"

    def verify(
        self,
        record: MemoryRecord,
        persistence: MemoryPersistenceResult,
    ) -> MemoryPersistenceVerificationResult:
        """Verify durable evidence independently from repository reporting."""

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

        expected_payload = encode_memory_record(record)

        try:
            durable_payload = self._evidence_reader.read_payload(
                record.memory_record_id
            )
        except Exception as exc:
            return MemoryPersistenceVerificationResult(
                memory_record_id=record.memory_record_id,
                repository_name=persistence.repository_name,
                state=VerificationState.UNKNOWN,
                verified_by=self.name,
                trace=record.trace,
                reason=(
                    "Durable memory evidence could not be determined: "
                    f"{type(exc).__name__}"
                ),
            )

        if durable_payload is None:
            return MemoryPersistenceVerificationResult(
                memory_record_id=record.memory_record_id,
                repository_name=persistence.repository_name,
                state=VerificationState.FAILED,
                verified_by=self.name,
                trace=record.trace,
                reason="Expected durable memory record is absent.",
            )

        if durable_payload != expected_payload:
            return MemoryPersistenceVerificationResult(
                memory_record_id=record.memory_record_id,
                repository_name=persistence.repository_name,
                state=VerificationState.FAILED,
                verified_by=self.name,
                trace=record.trace,
                reason="Durable memory payload does not match expected record.",
            )

        return MemoryPersistenceVerificationResult(
            memory_record_id=record.memory_record_id,
            repository_name=persistence.repository_name,
            state=VerificationState.VERIFIED,
            verified_by=self.name,
            trace=record.trace,
            reason="Observed expected durable memory record.",
        )