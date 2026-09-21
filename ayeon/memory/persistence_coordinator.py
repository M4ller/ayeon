"""Deterministic coordination for memory persistence."""

from __future__ import annotations

from ayeon.contracts.common import ResultState
from ayeon.contracts.memory import MemoryRecord
from ayeon.contracts.memory_persistence import MemoryPersistenceResult
from ayeon.memory.repository import MemoryRepository


class MemoryPersistenceCoordinator:
    """Coordinate persistence and validate repository result provenance."""

    def persist(
        self,
        record: MemoryRecord,
        repository: MemoryRepository,
    ) -> MemoryPersistenceResult:
        """Persist one record and validate the returned evidence."""

        try:
            result = repository.store(record)
        except Exception as exc:
            return MemoryPersistenceResult(
                memory_record_id=record.memory_record_id,
                repository_name=repository.name,
                state=ResultState.UNKNOWN,
                trace=record.trace,
                summary=(
                    "Memory repository raised an exception; "
                    "persistence state is unknown: "
                    f"{type(exc).__name__}"
                ),
            )

        if not isinstance(result, MemoryPersistenceResult):
            raise TypeError(
                "repository result must be MemoryPersistenceResult"
            )

        if result.memory_record_id != record.memory_record_id:
            raise ValueError("inconsistent persistence result: memory_record_id")

        if (
            result.trace.correlation_id
            != record.trace.correlation_id
        ):
            raise ValueError("inconsistent persistence result: correlation_id")

        if result.repository_name != repository.name:
            raise ValueError("inconsistent persistence result: repository_name")

        return result
