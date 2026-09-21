import pytest

from ayeon.contracts.common import (
    ResultState,
    TraceContext,
    new_memory_record_id,
)
from ayeon.contracts.memory import (
    AdmittedMemoryIntent,
    MemoryAdmissionDecision,
    MemoryAdmissionOutcome,
    MemoryIntent,
    MemoryRecord,
)
from ayeon.contracts.memory_persistence import MemoryPersistenceResult
from ayeon.memory.persistence_coordinator import MemoryPersistenceCoordinator


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


class ValidRepository:
    @property
    def name(self) -> str:
        return "valid_repository"

    def store(self, record: MemoryRecord) -> MemoryPersistenceResult:
        return MemoryPersistenceResult(
            memory_record_id=record.memory_record_id,
            repository_name=self.name,
            state=ResultState.SUCCESS,
            trace=record.trace,
            summary="Stored.",
        )


def test_coordinator_accepts_consistent_repository_result() -> None:
    record = make_record()
    coordinator = MemoryPersistenceCoordinator()

    result = coordinator.persist(record, ValidRepository())

    assert result.memory_record_id == record.memory_record_id
    assert result.trace is record.trace
    assert result.repository_name == "valid_repository"


@pytest.mark.parametrize(
    "mismatch",
    ["memory_record_id", "correlation_id", "repository_name"],
)
def test_coordinator_rejects_inconsistent_repository_result(
    mismatch: str,
) -> None:
    record = make_record()

    class InconsistentRepository:
        @property
        def name(self) -> str:
            return "expected_repository"

        def store(self, stored_record: MemoryRecord) -> MemoryPersistenceResult:
            memory_record_id = stored_record.memory_record_id
            trace = stored_record.trace
            repository_name = self.name

            if mismatch == "memory_record_id":
                memory_record_id = new_memory_record_id()
            elif mismatch == "correlation_id":
                trace = TraceContext.root()
            elif mismatch == "repository_name":
                repository_name = "different_repository"

            return MemoryPersistenceResult(
                memory_record_id=memory_record_id,
                repository_name=repository_name,
                state=ResultState.SUCCESS,
                trace=trace,
                summary="Stored.",
            )

    coordinator = MemoryPersistenceCoordinator()

    with pytest.raises(ValueError, match="inconsistent persistence result"):
        coordinator.persist(record, InconsistentRepository())


def test_coordinator_converts_repository_exception_to_unknown() -> None:
    record = make_record()

    class FailingRepository:
        @property
        def name(self) -> str:
            return "failing_repository"

        def store(self, stored_record: MemoryRecord) -> MemoryPersistenceResult:
            raise RuntimeError("simulated persistence failure")

    coordinator = MemoryPersistenceCoordinator()

    result = coordinator.persist(record, FailingRepository())

    assert result.memory_record_id == record.memory_record_id
    assert result.repository_name == "failing_repository"
    assert result.state is ResultState.UNKNOWN
    assert result.trace is record.trace
    assert "RuntimeError" in result.summary


def test_coordinator_rejects_invalid_repository_result_type() -> None:
    record = make_record()

    class InvalidRepository:
        @property
        def name(self) -> str:
            return "invalid_repository"

        def store(self, stored_record: MemoryRecord) -> MemoryPersistenceResult:
            return None  # type: ignore[return-value]

    coordinator = MemoryPersistenceCoordinator()

    with pytest.raises(
        TypeError,
        match="repository result must be MemoryPersistenceResult",
    ):
        coordinator.persist(record, InvalidRepository())
