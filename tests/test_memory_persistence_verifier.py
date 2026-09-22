from ayeon.contracts.common import ResultState, TraceContext
from ayeon.contracts.memory import (
    AdmittedMemoryIntent,
    MemoryAdmissionDecision,
    MemoryAdmissionOutcome,
    MemoryIntent,
    MemoryRecord,
)
from ayeon.contracts.memory_persistence import MemoryPersistenceResult
from ayeon.contracts.memory_persistence_verification import (
    MemoryPersistenceVerificationResult,
)
from ayeon.contracts.verification import VerificationState
from ayeon.memory.persistence_verifier import MemoryPersistenceVerifier


def make_record() -> MemoryRecord:
    trace = TraceContext.root()
    intent = MemoryIntent(
        content={"fact": "test"},
        proposed_by="test",
        trace=trace,
        reason="Test memory.",
    )
    admission = MemoryAdmissionDecision(
        memory_intent_id=intent.memory_intent_id,
        outcome=MemoryAdmissionOutcome.ACCEPT,
        decided_by="test",
        trace=trace,
        reason="Accepted for test.",
    )
    return MemoryRecord.from_admitted(
        AdmittedMemoryIntent(
            intent=intent,
            admission=admission,
        )
    )


class FakeMemoryPersistenceVerifier:
    @property
    def name(self) -> str:
        return "fake_memory_persistence_verifier"

    def verify(
        self,
        record: MemoryRecord,
        persistence: MemoryPersistenceResult,
    ) -> MemoryPersistenceVerificationResult:
        return MemoryPersistenceVerificationResult(
            memory_record_id=record.memory_record_id,
            repository_name=persistence.repository_name,
            state=VerificationState.VERIFIED,
            verified_by=self.name,
            trace=record.trace,
            reason="Observed expected durable memory record.",
        )


def test_memory_persistence_verifier_protocol_is_runtime_checkable() -> None:
    verifier = FakeMemoryPersistenceVerifier()

    assert isinstance(verifier, MemoryPersistenceVerifier)


def test_memory_persistence_verifier_returns_typed_evidence() -> None:
    record = make_record()
    persistence = MemoryPersistenceResult(
        memory_record_id=record.memory_record_id,
        repository_name="test_repository",
        state=ResultState.SUCCESS,
        trace=record.trace,
        summary="Stored.",
    )
    verifier = FakeMemoryPersistenceVerifier()

    result = verifier.verify(record, persistence)

    assert isinstance(result, MemoryPersistenceVerificationResult)
    assert result.memory_record_id == record.memory_record_id
    assert result.repository_name == persistence.repository_name
    assert result.verified_by == verifier.name