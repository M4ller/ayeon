from ayeon.contracts.common import TraceContext, new_memory_record_id
from ayeon.contracts.memory import (
    AdmittedMemoryIntent,
    MemoryAdmissionDecision,
    MemoryAdmissionOutcome,
    MemoryIntent,
    MemoryRecord,
)
from ayeon.memory.durable_evidence import DurableMemoryEvidenceReader
from ayeon.memory.serialization import encode_memory_record
from ayeon.memory.sqlite_evidence_reader import (
    SQLiteDurableMemoryEvidenceReader,
)
from ayeon.memory.sqlite_repository import SQLiteMemoryRepository


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


def test_sqlite_evidence_reader_satisfies_protocol(tmp_path) -> None:
    reader = SQLiteDurableMemoryEvidenceReader(
        tmp_path / "memory.db"
    )

    assert isinstance(reader, DurableMemoryEvidenceReader)


def test_sqlite_evidence_reader_returns_exact_durable_payload(
    tmp_path,
) -> None:
    database_path = tmp_path / "memory.db"
    repository = SQLiteMemoryRepository(database_path)
    record = make_record()

    repository.store(record)

    reader = SQLiteDurableMemoryEvidenceReader(database_path)

    assert reader.read_payload(
        record.memory_record_id
    ) == encode_memory_record(record)


def test_sqlite_evidence_reader_returns_none_for_confirmed_absence(
    tmp_path,
) -> None:
    database_path = tmp_path / "memory.db"
    SQLiteMemoryRepository(database_path)
    reader = SQLiteDurableMemoryEvidenceReader(database_path)

    assert reader.read_payload(new_memory_record_id()) is None

def test_sqlite_evidence_reader_does_not_create_missing_database(
    tmp_path,
) -> None:
    database_path = tmp_path / "missing.db"
    reader = SQLiteDurableMemoryEvidenceReader(database_path)

    assert not database_path.exists()

    try:
        reader.read_payload(new_memory_record_id())
    except Exception:
        pass
    else:
        raise AssertionError(
            "Read-only evidence lookup unexpectedly succeeded."
        )

    assert not database_path.exists()

def test_sqlite_evidence_reader_rejects_unsupported_schema_version(
    tmp_path,
) -> None:
    database_path = tmp_path / "memory.db"
    repository = SQLiteMemoryRepository(database_path)
    record = make_record()
    repository.store(record)

    import sqlite3

    with sqlite3.connect(database_path) as connection:
        connection.execute("PRAGMA user_version = 2")

    reader = SQLiteDurableMemoryEvidenceReader(database_path)

    try:
        reader.read_payload(record.memory_record_id)
    except RuntimeError as exc:
        assert "schema version" in str(exc).lower()
    else:
        raise AssertionError(
            "Unsupported SQLite schema version was trusted."
        )

def test_sqlite_evidence_reader_releases_database_after_read(
    tmp_path,
) -> None:
    database_path = tmp_path / "memory.db"
    repository = SQLiteMemoryRepository(database_path)
    record = make_record()
    repository.store(record)

    reader = SQLiteDurableMemoryEvidenceReader(database_path)

    assert reader.read_payload(
        record.memory_record_id
    ) == encode_memory_record(record)

    database_path.unlink()

    assert not database_path.exists()
