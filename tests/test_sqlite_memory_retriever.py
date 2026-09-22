import sqlite3

from ayeon.contracts.common import TraceContext, new_memory_record_id
from ayeon.contracts.memory import (
    AdmittedMemoryIntent,
    MemoryAdmissionDecision,
    MemoryAdmissionOutcome,
    MemoryIntent,
    MemoryRecord,
)
from ayeon.contracts.memory_retrieval import MemoryRetrievalOutcome
from ayeon.memory.retriever import MemoryRetriever
from ayeon.memory.serialization import encode_memory_record
from ayeon.memory.sqlite_repository import SQLiteMemoryRepository
from ayeon.memory.sqlite_retriever import SQLiteMemoryRetriever


def make_record() -> MemoryRecord:
    trace = TraceContext.root()
    intent = MemoryIntent(
        content={"fact": "portable-first"},
        proposed_by="cognition",
        trace=trace,
        reason="Test durable retrieval.",
    )
    admission = MemoryAdmissionDecision(
        memory_intent_id=intent.memory_intent_id,
        outcome=MemoryAdmissionOutcome.ACCEPT,
        decided_by="memory_intake_policy",
        trace=trace,
        reason="Accepted for retrieval test.",
    )
    return MemoryRecord.from_admitted(
        AdmittedMemoryIntent(
            intent=intent,
            admission=admission,
        )
    )


def test_sqlite_memory_retriever_satisfies_protocol(tmp_path) -> None:
    retriever = SQLiteMemoryRetriever(tmp_path / "memory.db")

    assert isinstance(retriever, MemoryRetriever)


def test_sqlite_memory_retriever_returns_found_payload(tmp_path) -> None:
    database_path = tmp_path / "memory.db"
    repository = SQLiteMemoryRepository(database_path)
    record = make_record()
    repository.store(record)

    result = SQLiteMemoryRetriever(database_path).retrieve(
        record.memory_record_id
    )

    assert result.memory_record_id == record.memory_record_id
    assert result.outcome is MemoryRetrievalOutcome.FOUND
    assert result.payload == encode_memory_record(record)
    assert result.retrieved_by == "sqlite_memory_retriever"


def test_sqlite_memory_retriever_returns_not_found_for_absent_record(
    tmp_path,
) -> None:
    database_path = tmp_path / "memory.db"
    SQLiteMemoryRepository(database_path)

    memory_record_id = new_memory_record_id()

    result = SQLiteMemoryRetriever(database_path).retrieve(
        memory_record_id
    )

    assert result.memory_record_id == memory_record_id
    assert result.outcome is MemoryRetrievalOutcome.NOT_FOUND
    assert result.payload is None


def test_sqlite_memory_retriever_returns_unknown_for_missing_database(
    tmp_path,
) -> None:
    database_path = tmp_path / "missing.db"
    memory_record_id = new_memory_record_id()

    result = SQLiteMemoryRetriever(database_path).retrieve(
        memory_record_id
    )

    assert result.memory_record_id == memory_record_id
    assert result.outcome is MemoryRetrievalOutcome.UNKNOWN
    assert result.payload is None
    assert not database_path.exists()

def test_sqlite_memory_retriever_returns_unknown_for_future_schema(
    tmp_path,
) -> None:
    database_path = tmp_path / "memory.db"
    SQLiteMemoryRepository(database_path)
    memory_record_id = new_memory_record_id()

    with sqlite3.connect(database_path) as connection:
        connection.execute("PRAGMA user_version = 2")

    result = SQLiteMemoryRetriever(database_path).retrieve(
        memory_record_id
    )

    assert result.memory_record_id == memory_record_id
    assert result.outcome is MemoryRetrievalOutcome.UNKNOWN
    assert result.payload is None
    assert "RuntimeError" in result.reason

def test_sqlite_memory_retriever_releases_database_after_found(
    tmp_path,
) -> None:
    database_path = tmp_path / "memory.db"
    repository = SQLiteMemoryRepository(database_path)
    record = make_record()
    repository.store(record)

    result = SQLiteMemoryRetriever(database_path).retrieve(
        record.memory_record_id
    )

    assert result.outcome is MemoryRetrievalOutcome.FOUND

    database_path.unlink()

    assert not database_path.exists()
