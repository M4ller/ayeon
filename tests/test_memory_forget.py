"""Tests for removing a specific durable memory record."""

import sqlite3

from test_sqlite_memory_repository import make_record

from ayeon.memory.record_reference_store import LocalMemoryReferenceStore
from ayeon.memory.serialization import encode_memory_record
from ayeon.memory.sqlite_repository import SQLiteMemoryRepository


def test_remove_one_record_preserves_another(tmp_path) -> None:
    database = tmp_path / "memory.db"
    references = LocalMemoryReferenceStore(tmp_path / "memory.references.jsonl")
    repository = SQLiteMemoryRepository(database)
    target = make_record()
    other = make_record()

    for record in (target, other):
        repository.store(record)
        references.append(record)

    assert references.remove(target) is True
    assert repository.delete(target) is True
    assert [record.memory_record_id for record in references.load()] == [
        other.memory_record_id
    ]

    with sqlite3.connect(database) as connection:
        rows = connection.execute(
            "SELECT memory_record_id FROM memory_records"
        ).fetchall()
    assert rows == [(str(other.memory_record_id),)]


def test_delete_rejects_changed_sqlite_payload(tmp_path) -> None:
    database = tmp_path / "memory.db"
    repository = SQLiteMemoryRepository(database)
    target = make_record()
    repository.store(target)

    with sqlite3.connect(database) as connection:
        connection.execute(
            "UPDATE memory_records SET record_payload = ? "
            "WHERE memory_record_id = ?",
            (b"changed", str(target.memory_record_id)),
        )

    assert repository.delete(target) is False
    with sqlite3.connect(database) as connection:
        stored = connection.execute(
            "SELECT record_payload FROM memory_records WHERE memory_record_id = ?",
            (str(target.memory_record_id),),
        ).fetchone()
    assert stored == (b"changed",)
    assert encode_memory_record(target) != stored[0]
