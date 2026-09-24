"""Independent comparison of retrieved bytes with durable evidence."""

from __future__ import annotations

from ayeon.contracts.memory_retrieval_decoding import (
    MemoryDecodeOutcome,
    MemoryRetrievalDecodingResult,
)
from ayeon.contracts.memory_retrieval_verification import (
    MemoryRetrievalVerificationResult,
)
from ayeon.contracts.verification import VerificationState
from ayeon.memory.durable_evidence import DurableMemoryEvidenceReader


class MemoryRetrievalVerifier:
    """Check byte consistency without claiming content authenticity."""

    def __init__(self, reader: DurableMemoryEvidenceReader) -> None:
        self._reader = reader

    @property
    def name(self) -> str:
        return "memory_retrieval_verifier"

    def verify(
        self,
        decoding: MemoryRetrievalDecodingResult,
    ) -> MemoryRetrievalVerificationResult:
        if decoding.outcome is not MemoryDecodeOutcome.DECODED:
            return MemoryRetrievalVerificationResult(
                decoding=decoding,
                state=VerificationState.UNKNOWN,
                verified_by=self.name,
                reason="Retrieved memory was not decoded.",
            )

        retrieval = decoding.retrieval
        try:
            durable_payload = self._reader.read_payload(
                retrieval.memory_record_id
            )
        except Exception as exc:
            return MemoryRetrievalVerificationResult(
                decoding=decoding,
                state=VerificationState.UNKNOWN,
                verified_by=self.name,
                reason=f"Durable evidence unavailable: {type(exc).__name__}.",
            )

        if durable_payload != retrieval.payload:
            return MemoryRetrievalVerificationResult(
                decoding=decoding,
                state=VerificationState.FAILED,
                verified_by=self.name,
                reason="Durable bytes differ from retrieved bytes.",
            )

        return MemoryRetrievalVerificationResult(
            decoding=decoding,
            state=VerificationState.VERIFIED,
            verified_by=self.name,
            reason="Independent durable bytes match retrieved bytes.",
        )
