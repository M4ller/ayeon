from datetime import datetime

import pytest

from ayeon.contracts.common import ResultState, TraceContext, new_memory_record_id
from ayeon.contracts.memory_persistence import MemoryPersistenceResult


def test_memory_persistence_result_preserves_evidence() -> None:
    trace = TraceContext.root()
    memory_record_id = new_memory_record_id()

    result = MemoryPersistenceResult(
        memory_record_id=memory_record_id,
        repository_name="test_repository",
        state=ResultState.SUCCESS,
        trace=trace,
        summary="Memory record stored.",
    )

    assert result.memory_record_id == memory_record_id
    assert result.repository_name == "test_repository"
    assert result.state is ResultState.SUCCESS
    assert result.trace is trace
    assert result.summary == "Memory record stored."
    assert isinstance(result.completed_at, datetime)
    assert result.completed_at.tzinfo is not None


def test_memory_persistence_result_rejects_empty_repository_name() -> None:
    with pytest.raises(
        ValueError,
        match="repository_name must not be empty",
    ):
        MemoryPersistenceResult(
            memory_record_id=new_memory_record_id(),
            repository_name=" ",
            state=ResultState.SUCCESS,
            trace=TraceContext.root(),
            summary="Stored.",
        )


def test_memory_persistence_result_rejects_empty_summary() -> None:
    with pytest.raises(ValueError, match="summary must not be empty"):
        MemoryPersistenceResult(
            memory_record_id=new_memory_record_id(),
            repository_name="test_repository",
            state=ResultState.FAILED,
            trace=TraceContext.root(),
            summary=" ",
        )


def test_memory_persistence_result_rejects_invalid_state() -> None:
    with pytest.raises(TypeError, match="state must be ResultState"):
        MemoryPersistenceResult(
            memory_record_id=new_memory_record_id(),
            repository_name="test_repository",
            state="success",
            trace=TraceContext.root(),
            summary="Stored.",
        )
