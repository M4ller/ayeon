from dataclasses import replace

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
from ayeon.contracts.memory_persistence_result_verification import (
    MemoryPersistenceResultVerification,
)
from ayeon.contracts.memory_persistence_verification import (
    MemoryPersistenceVerificationResult,
)
from ayeon.contracts.verification import VerificationState
from ayeon.memory.persistence_verification_coordinator import (
    MemoryPersistenceVerificationCoordinator,
)


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


class StubVerifier:
    name = "stub_verifier"

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
            reason="Verified.",
        )


def test_coordinator_returns_valid_association() -> None:
    record = make_record()
    persistence = make_persistence(record)

    result = MemoryPersistenceVerificationCoordinator().verify(
        record,
        persistence,
        StubVerifier(),
    )

    assert isinstance(result, MemoryPersistenceResultVerification)
    assert result.persistence is persistence
    assert result.verification.state is VerificationState.VERIFIED


def test_coordinator_maps_verifier_exception_to_unknown() -> None:
    record = make_record()
    persistence = make_persistence(record)

    class RaisingVerifier(StubVerifier):
        name = "raising_verifier"

        def verify(self, record, persistence):
            raise RuntimeError("boom")

    result = MemoryPersistenceVerificationCoordinator().verify(
        record,
        persistence,
        RaisingVerifier(),
    )

    assert result.verification.state is VerificationState.UNKNOWN
    assert result.verification.verified_by == "raising_verifier"
    assert "RuntimeError" in result.verification.reason


def test_coordinator_rejects_wrong_result_type() -> None:
    record = make_record()
    persistence = make_persistence(record)

    class InvalidVerifier(StubVerifier):
        def verify(self, record, persistence):
            return object()

    with pytest.raises(TypeError):
        MemoryPersistenceVerificationCoordinator().verify(
            record,
            persistence,
            InvalidVerifier(),
        )


def test_coordinator_rejects_wrong_verified_by() -> None:
    record = make_record()
    persistence = make_persistence(record)

    class WrongVerifier(StubVerifier):
        def verify(self, record, persistence):
            result = super().verify(record, persistence)
            return replace(result, verified_by="different_verifier")

    with pytest.raises(ValueError, match="verified_by"):
        MemoryPersistenceVerificationCoordinator().verify(
            record,
            persistence,
            WrongVerifier(),
        )

def test_coordinator_rejects_wrong_memory_record_id() -> None:
    record = make_record()
    persistence = make_persistence(record)
    other_record = make_record()

    class WrongVerifier(StubVerifier):
        def verify(self, record, persistence):
            result = super().verify(record, persistence)
            return replace(
                result,
                memory_record_id=other_record.memory_record_id,
            )

    with pytest.raises(ValueError, match="memory_record_id"):
        MemoryPersistenceVerificationCoordinator().verify(
            record,
            persistence,
            WrongVerifier(),
        )


def test_coordinator_rejects_wrong_repository_name() -> None:
    record = make_record()
    persistence = make_persistence(record)

    class WrongVerifier(StubVerifier):
        def verify(self, record, persistence):
            result = super().verify(record, persistence)
            return replace(
                result,
                repository_name="different_repository",
            )

    with pytest.raises(ValueError, match="repository_name"):
        MemoryPersistenceVerificationCoordinator().verify(
            record,
            persistence,
            WrongVerifier(),
        )


def test_coordinator_rejects_wrong_correlation_id() -> None:
    record = make_record()
    persistence = make_persistence(record)
    other_trace = TraceContext.root()

    class WrongVerifier(StubVerifier):
        def verify(self, record, persistence):
            result = super().verify(record, persistence)
            return replace(
                result,
                trace=other_trace,
            )

    with pytest.raises(ValueError, match="correlation"):
        MemoryPersistenceVerificationCoordinator().verify(
            record,
            persistence,
            WrongVerifier(),
        )

def test_coordinator_rejects_persistence_for_different_record() -> None:
    record = make_record()
    other_record = make_record()
    persistence = make_persistence(other_record)

    class MustNotRunVerifier(StubVerifier):
        called = False

        def verify(self, record, persistence):
            self.called = True
            raise AssertionError("verifier must not run")

    verifier = MustNotRunVerifier()

    with pytest.raises(
        ValueError,
        match="memory_record_id",
    ):
        MemoryPersistenceVerificationCoordinator().verify(
            record,
            persistence,
            verifier,
        )

    assert verifier.called is False


def test_coordinator_rejects_persistence_with_wrong_correlation() -> None:
    record = make_record()
    other_trace = TraceContext.root()
    persistence = replace(
        make_persistence(record),
        trace=other_trace,
    )

    class MustNotRunVerifier(StubVerifier):
        called = False

        def verify(self, record, persistence):
            self.called = True
            raise AssertionError("verifier must not run")

    verifier = MustNotRunVerifier()

    with pytest.raises(
        ValueError,
        match="correlation_id",
    ):
        MemoryPersistenceVerificationCoordinator().verify(
            record,
            persistence,
            verifier,
        )

    assert verifier.called is False
