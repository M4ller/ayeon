"""Integration tests for durable memory retrieval and decoding."""

from test_sqlite_memory_repository import make_record

from ayeon.contracts.common import ResultState
from ayeon.contracts.memory_retrieval_decoding import MemoryDecodeOutcome
from ayeon.memory.retrieval_decoding_coordinator import (
    MemoryRetrievalDecodingCoordinator,
)
from ayeon.memory.sqlite_repository import SQLiteMemoryRepository
from ayeon.memory.sqlite_retriever import SQLiteMemoryRetriever


def test_stored_memory_can_be_retrieved_and_decoded(tmp_path) -> None:
    database_path = tmp_path / "memory.db"
    record = make_record()
    persistence = SQLiteMemoryRepository(database_path).store(record)

    assert persistence.state is ResultState.SUCCESS

    result = MemoryRetrievalDecodingCoordinator().retrieve_and_decode(
        record.memory_record_id,
        SQLiteMemoryRetriever(database_path),
    )

    assert result.outcome is MemoryDecodeOutcome.DECODED
    assert result.decoded is not None
    assert result.decoded.memory_record_id == record.memory_record_id
    assert result.decoded.content == record.content

def test_corrupt_stored_payload_returns_unknown(tmp_path) -> None:
    import sqlite3

    database_path = tmp_path / "memory.db"
    record = make_record()
    SQLiteMemoryRepository(database_path).store(record)

    with sqlite3.connect(database_path) as connection:
        connection.execute(
            """
            UPDATE memory_records
            SET record_payload = ?
            WHERE memory_record_id = ?
            """,
            (b"invalid payload", str(record.memory_record_id)),
        )

    result = MemoryRetrievalDecodingCoordinator().retrieve_and_decode(
        record.memory_record_id,
        SQLiteMemoryRetriever(database_path),
    )

    assert result.outcome is MemoryDecodeOutcome.UNKNOWN
    assert result.decoded is None
