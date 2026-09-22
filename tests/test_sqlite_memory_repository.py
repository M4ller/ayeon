import sqlite3
from datetime import timedelta

from ayeon.contracts.common import ResultState, TraceContext
from ayeon.contracts.memory import (
    AdmittedMemoryIntent,
    MemoryAdmissionDecision,
    MemoryAdmissionOutcome,
    MemoryIntent,
    MemoryRecord,
)
from ayeon.memory.sqlite_repository import SQLiteMemoryRepository


def make_record() -> MemoryRecord:
    trace = TraceContext.root()
    intent = MemoryIntent(
        content={"fact": "portable-first"},
        proposed_by="cognition",
        trace=trace,
        reason="Test durable persistence.",
    )
    admission = MemoryAdmissionDecision(
        memory_intent_id=intent.memory_intent_id,
        outcome=MemoryAdmissionOutcome.ACCEPT,
        decided_by="memory_intake_policy",
        trace=trace,
        reason="Accepted for persistence test.",
    )
    return MemoryRecord.from_admitted(
        AdmittedMemoryIntent(
            intent=intent,
            admission=admission,
        )
    )


def test_sqlite_repository_stores_record_idempotently(tmp_path) -> None:
    repository = SQLiteMemoryRepository(tmp_path / "memory.db")
    record = make_record()

    first = repository.store(record)
    repeated = repository.store(record)

    assert first.state is ResultState.SUCCESS
    assert repeated.state is ResultState.SUCCESS
    assert first.memory_record_id == record.memory_record_id
    assert repeated.memory_record_id == record.memory_record_id


def test_sqlite_repository_rejects_conflicting_record_identity(tmp_path) -> None:
    repository = SQLiteMemoryRepository(tmp_path / "memory.db")
    original = make_record()
    conflicting = MemoryRecord(
        admitted=original.admitted,
        memory_record_id=original.memory_record_id,
        created_at=original.created_at + timedelta(seconds=1),
    )

    first = repository.store(original)
    conflict = repository.store(conflicting)

    assert first.state is ResultState.SUCCESS
    assert conflict.state is ResultState.FAILED
    assert conflict.memory_record_id == original.memory_record_id

def test_sqlite_repository_record_survives_repository_reopen(tmp_path) -> None:
    database_path = tmp_path / "memory.db"
    record = make_record()

    repository = SQLiteMemoryRepository(database_path)
    result = repository.store(record)

    assert result.state is ResultState.SUCCESS

    reopened_repository = SQLiteMemoryRepository(database_path)
    repeated = reopened_repository.store(record)

    assert repeated.state is ResultState.SUCCESS
    assert "already stored identically" in repeated.summary


def test_sqlite_repository_conflict_does_not_overwrite_original(tmp_path) -> None:
    database_path = tmp_path / "memory.db"
    repository = SQLiteMemoryRepository(database_path)
    original = make_record()
    conflicting = MemoryRecord(
        admitted=original.admitted,
        memory_record_id=original.memory_record_id,
        created_at=original.created_at + timedelta(seconds=1),
    )

    first = repository.store(original)
    conflict = repository.store(conflicting)

    assert first.state is ResultState.SUCCESS
    assert conflict.state is ResultState.FAILED

    with sqlite3.connect(database_path) as connection:
        stored_payload = connection.execute(
            """
            SELECT record_payload
            FROM memory_records
            WHERE memory_record_id = ?
            """,
            (str(original.memory_record_id),),
        ).fetchone()

    assert stored_payload is not None

    from ayeon.memory.serialization import encode_memory_record

    assert bytes(stored_payload[0]) == encode_memory_record(original)
    assert bytes(stored_payload[0]) != encode_memory_record(conflicting)

def test_sqlite_repository_connections_use_full_synchronous(tmp_path) -> None:
    repository = SQLiteMemoryRepository(tmp_path / "memory.db")

    with repository._connect() as connection:
        synchronous = connection.execute(
            "PRAGMA synchronous"
        ).fetchone()[0]

    assert synchronous == 2

def test_sqlite_repository_connect_enforces_full_synchronous(
    tmp_path,
    monkeypatch,
) -> None:
    database_path = tmp_path / "memory.db"
    real_connect = sqlite3.connect

    def connect_with_degraded_policy(*args, **kwargs):
        connection = real_connect(*args, **kwargs)
        connection.execute("PRAGMA synchronous = OFF")
        return connection

    monkeypatch.setattr(
        "ayeon.memory.sqlite_repository.sqlite3.connect",
        connect_with_degraded_policy,
    )

    repository = SQLiteMemoryRepository(database_path)

    with repository._connect() as connection:
        synchronous = connection.execute(
            "PRAGMA synchronous"
        ).fetchone()[0]

    assert synchronous == 2

def test_sqlite_repository_uses_delete_journal_mode(tmp_path) -> None:
    database_path = tmp_path / "memory.db"

    SQLiteMemoryRepository(database_path)

    with sqlite3.connect(database_path) as connection:
        journal_mode = connection.execute(
            "PRAGMA journal_mode"
        ).fetchone()[0]

    assert journal_mode == "delete"

def test_sqlite_repository_enforces_delete_journal_mode(tmp_path) -> None:
    database_path = tmp_path / "memory.db"

    with sqlite3.connect(database_path) as connection:
        configured_mode = connection.execute(
            "PRAGMA journal_mode = WAL"
        ).fetchone()[0]

    assert configured_mode == "wal"

    SQLiteMemoryRepository(database_path)

    with sqlite3.connect(database_path) as connection:
        journal_mode = connection.execute(
            "PRAGMA journal_mode"
        ).fetchone()[0]

    assert journal_mode == "delete"

def test_sqlite_repository_initializes_schema_version_one(tmp_path) -> None:
    database_path = tmp_path / "memory.db"

    SQLiteMemoryRepository(database_path)

    with sqlite3.connect(database_path) as connection:
        schema_version = connection.execute(
            "PRAGMA user_version"
        ).fetchone()[0]

    assert schema_version == 1

def test_sqlite_repository_rejects_unknown_future_schema_version(
    tmp_path,
) -> None:
    database_path = tmp_path / "memory.db"

    with sqlite3.connect(database_path) as connection:
        connection.execute("PRAGMA user_version = 2")

    try:
        SQLiteMemoryRepository(database_path)
    except RuntimeError as error:
        assert str(error) == "Unsupported SQLite schema version: 2."
    else:
        raise AssertionError(
            "Repository accepted an unsupported schema version."
        )

    with sqlite3.connect(database_path) as connection:
        schema_version = connection.execute(
            "PRAGMA user_version"
        ).fetchone()[0]

    assert schema_version == 2

def test_sqlite_repository_reopens_version_one_without_losing_data(
    tmp_path,
) -> None:
    database_path = tmp_path / "memory.db"
    record = make_record()

    first_repository = SQLiteMemoryRepository(database_path)
    stored = first_repository.store(record)

    assert stored.state is ResultState.SUCCESS

    reopened_repository = SQLiteMemoryRepository(database_path)
    repeated = reopened_repository.store(record)

    assert repeated.state is ResultState.SUCCESS
    assert "already stored identically" in repeated.summary

    with sqlite3.connect(database_path) as connection:
        schema_version = connection.execute(
            "PRAGMA user_version"
        ).fetchone()[0]
        row_count = connection.execute(
            "SELECT COUNT(*) FROM memory_records"
        ).fetchone()[0]

    assert schema_version == 1
    assert row_count == 1

def test_sqlite_schema_bootstrap_runs_inside_explicit_transaction(
    tmp_path,
    monkeypatch,
) -> None:
    database_path = tmp_path / "memory.db"
    real_connect = sqlite3.connect
    transaction_states: list[bool] = []

    class ObservedConnection(sqlite3.Connection):
        def execute(self, sql, parameters=()):
            if "CREATE TABLE IF NOT EXISTS memory_records" in sql:
                transaction_states.append(self.in_transaction)
            return super().execute(sql, parameters)

    def observed_connect(*args, **kwargs):
        kwargs["factory"] = ObservedConnection
        return real_connect(*args, **kwargs)

    monkeypatch.setattr(
        "ayeon.memory.sqlite_repository.sqlite3.connect",
        observed_connect,
    )

    SQLiteMemoryRepository(database_path)

    assert transaction_states == [True]

def test_sqlite_schema_bootstrap_rolls_back_on_failure(
    tmp_path,
    monkeypatch,
) -> None:
    database_path = tmp_path / "memory.db"
    real_connect = sqlite3.connect

    class FailingBootstrapConnection(sqlite3.Connection):
        def execute(self, sql, parameters=()):
            if sql.strip() == "PRAGMA user_version = 1":
                raise RuntimeError("simulated bootstrap failure")
            return super().execute(sql, parameters)

    def failing_connect(*args, **kwargs):
        kwargs["factory"] = FailingBootstrapConnection
        return real_connect(*args, **kwargs)

    monkeypatch.setattr(
        "ayeon.memory.sqlite_repository.sqlite3.connect",
        failing_connect,
    )

    try:
        SQLiteMemoryRepository(database_path)
    except RuntimeError as error:
        assert str(error) == "simulated bootstrap failure"
    else:
        raise AssertionError(
            "Repository bootstrap unexpectedly succeeded."
        )

    with real_connect(database_path) as connection:
        schema_version = connection.execute(
            "PRAGMA user_version"
        ).fetchone()[0]
        table = connection.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
              AND name = 'memory_records'
            """
        ).fetchone()

    assert schema_version == 0
    assert table is None

def test_sqlite_store_rolls_back_when_failure_occurs_after_insert(
    tmp_path,
    monkeypatch,
) -> None:
    database_path = tmp_path / "memory.db"
    repository = SQLiteMemoryRepository(database_path)
    record = make_record()
    real_connect = sqlite3.connect

    class FailingStoreConnection(sqlite3.Connection):
        def execute(self, sql, parameters=()):
            cursor = super().execute(sql, parameters)

            if "INSERT INTO memory_records" in sql:
                raise RuntimeError("simulated failure after insert")

            return cursor

    def failing_connect(*args, **kwargs):
        kwargs["factory"] = FailingStoreConnection
        return real_connect(*args, **kwargs)

    monkeypatch.setattr(
        "ayeon.memory.sqlite_repository.sqlite3.connect",
        failing_connect,
    )

    try:
        repository.store(record)
    except RuntimeError as error:
        assert str(error) == "simulated failure after insert"
    else:
        raise AssertionError(
            "Repository store unexpectedly succeeded."
        )

    with real_connect(database_path) as connection:
        row = connection.execute(
            """
            SELECT memory_record_id
            FROM memory_records
            WHERE memory_record_id = ?
            """,
            (str(record.memory_record_id),),
        ).fetchone()

    assert row is None

def test_sqlite_repository_releases_database_after_initialization(
    tmp_path,
) -> None:
    database_path = tmp_path / "memory.db"

    SQLiteMemoryRepository(database_path)

    database_path.unlink()

    assert not database_path.exists()

def test_sqlite_repository_releases_database_after_store(
    tmp_path,
) -> None:
    database_path = tmp_path / "memory.db"
    repository = SQLiteMemoryRepository(database_path)
    record = make_record()

    result = repository.store(record)

    assert result.state is ResultState.SUCCESS

    database_path.unlink()

    assert not database_path.exists()
