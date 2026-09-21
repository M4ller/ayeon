from typing import runtime_checkable

from ayeon.contracts.common import ResultState
from ayeon.contracts.memory import MemoryRecord
from ayeon.contracts.memory_persistence import MemoryPersistenceResult
from ayeon.memory.repository import MemoryRepository


class FakeMemoryRepository:
    @property
    def name(self) -> str:
        return "fake_memory_repository"

    def store(self, record: MemoryRecord) -> MemoryPersistenceResult:
        return MemoryPersistenceResult(
            memory_record_id=record.memory_record_id,
            repository_name=self.name,
            state=ResultState.SUCCESS,
            trace=record.trace,
            summary="Memory record stored.",
        )


def test_memory_repository_is_runtime_checkable() -> None:
    assert runtime_checkable is not None
    assert isinstance(FakeMemoryRepository(), MemoryRepository)


def test_memory_repository_preserves_record_identity_and_trace() -> None:
    repository = FakeMemoryRepository()

    assert repository.name == "fake_memory_repository"

    annotations = repository.store.__annotations__

    assert annotations["record"] is MemoryRecord
    assert annotations["return"] is MemoryPersistenceResult
