import pytest

from ayeon.contracts.common import ResultState, TraceContext
from ayeon.contracts.memory import (
    AdmittedMemoryIntent,
    MemoryAdmissionDecision,
    MemoryAdmissionOutcome,
    MemoryIntent,
    MemoryRecord,
)
from ayeon.contracts.memory_persistence import MemoryPersistenceResult
from ayeon.contracts.verification import VerificationState
from ayeon.memory.deterministic_persistence_verifier import (
    DeterministicMemoryPersistenceVerifier,
)
from ayeon.memory.serialization import encode_memory_record


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


def make_persistence(
    record: MemoryRecord,
) -> MemoryPersistenceResult:
    return MemoryPersistenceResult(
        memory_record_id=record.memory_record_id,
        repository_name="test_repository",
        state=ResultState.SUCCESS,
        trace=record.trace,
        summary="Stored.",
    )


class FakeEvidenceReader:
    def __init__(
        self,
        payload: bytes | None = None,
        error: Exception | None = None,
    ) -> None:
        self._payload = payload
        self._error = error

    @property
    def name(self) -> str:
        return "fake_evidence_reader"

    def read_payload(self, memory_record_id):
        if self._error is not None:
            raise self._error
        return self._payload


def test_verifier_reports_verified_for_identical_durable_payload() -> None:
    record = make_record()
    persistence = make_persistence(record)
    reader = FakeEvidenceReader(
        payload=encode_memory_record(record),
    )
    verifier = DeterministicMemoryPersistenceVerifier(reader)

    result = verifier.verify(record, persistence)

    assert result.state is VerificationState.VERIFIED
    assert result.memory_record_id == record.memory_record_id
    assert result.repository_name == persistence.repository_name
    assert result.trace is record.trace
    assert result.verified_by == verifier.name


@pytest.mark.parametrize(
    ("payload", "expected_reason"),
    [
        (None, "absent"),
        (b"different durable payload", "does not match"),
    ],
)
def test_verifier_reports_failed_for_confirmed_bad_evidence(
    payload: bytes | None,
    expected_reason: str,
) -> None:
    record = make_record()
    persistence = make_persistence(record)
    verifier = DeterministicMemoryPersistenceVerifier(
        FakeEvidenceReader(payload=payload)
    )

    result = verifier.verify(record, persistence)

    assert result.state is VerificationState.FAILED
    assert expected_reason in result.reason.lower()


def test_verifier_reports_unknown_when_evidence_reader_raises() -> None:
    record = make_record()
    persistence = make_persistence(record)
    verifier = DeterministicMemoryPersistenceVerifier(
        FakeEvidenceReader(error=RuntimeError("simulated read failure"))
    )

    result = verifier.verify(record, persistence)

    assert result.state is VerificationState.UNKNOWN
    assert "RuntimeError" in result.reason

@pytest.mark.parametrize(
    "mismatch",
    ["memory_record_id", "correlation_id"],
)
def test_verifier_rejects_inconsistent_persistence_provenance(
    mismatch: str,
) -> None:
    record = make_record()

    memory_record_id = record.memory_record_id
    trace = record.trace

    if mismatch == "memory_record_id":
        other_record = make_record()
        memory_record_id = other_record.memory_record_id
    elif mismatch == "correlation_id":
        trace = TraceContext.root()

    persistence = MemoryPersistenceResult(
        memory_record_id=memory_record_id,
        repository_name="test_repository",
        state=ResultState.SUCCESS,
        trace=trace,
        summary="Stored.",
    )

    verifier = DeterministicMemoryPersistenceVerifier(
        FakeEvidenceReader(payload=encode_memory_record(record))
    )

    with pytest.raises(
        ValueError,
        match=f"inconsistent persistence result: {mismatch}",
    ):
        verifier.verify(record, persistence)
