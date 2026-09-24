"""Tests for independent verification of retrieved memory bytes."""

from test_sqlite_memory_repository import make_record

from ayeon.contracts.memory_retrieval_decoding import MemoryDecodeOutcome
from ayeon.contracts.verification import VerificationState
from ayeon.memory.retrieval_decoding_coordinator import (
    MemoryRetrievalDecodingCoordinator,
)
from ayeon.memory.retrieval_verifier import MemoryRetrievalVerifier
from ayeon.memory.sqlite_evidence_reader import SQLiteDurableMemoryEvidenceReader
from ayeon.memory.sqlite_repository import SQLiteMemoryRepository
from ayeon.memory.sqlite_retriever import SQLiteMemoryRetriever


def test_independent_reader_confirms_retrieved_bytes(tmp_path) -> None:
    database_path = tmp_path / "memory.db"
    record = make_record()
    SQLiteMemoryRepository(database_path).store(record)

    decoding = MemoryRetrievalDecodingCoordinator().retrieve_and_decode(
        record.memory_record_id,
        SQLiteMemoryRetriever(database_path),
    )
    verification = MemoryRetrievalVerifier(
        SQLiteDurableMemoryEvidenceReader(database_path)
    ).verify(decoding)

    assert decoding.outcome is MemoryDecodeOutcome.DECODED
    assert verification.state is VerificationState.VERIFIED
    assert verification.memory_record_id == record.memory_record_id

def test_independent_reader_detects_changed_bytes(tmp_path) -> None:
    import sqlite3

    database_path = tmp_path / "memory.db"
    record = make_record()
    SQLiteMemoryRepository(database_path).store(record)
    decoding = MemoryRetrievalDecodingCoordinator().retrieve_and_decode(
        record.memory_record_id,
        SQLiteMemoryRetriever(database_path),
    )

    with sqlite3.connect(database_path) as connection:
        connection.execute(
            """
            UPDATE memory_records
            SET record_payload = ?
            WHERE memory_record_id = ?
            """,
            (b"changed after retrieval", str(record.memory_record_id)),
        )

    verification = MemoryRetrievalVerifier(
        SQLiteDurableMemoryEvidenceReader(database_path)
    ).verify(decoding)

    assert verification.state is VerificationState.FAILED
    assert verification.decoding is decoding


def test_independent_reader_reports_unknown_when_storage_disappears(
    tmp_path,
) -> None:
    database_path = tmp_path / "memory.db"
    record = make_record()
    SQLiteMemoryRepository(database_path).store(record)
    decoding = MemoryRetrievalDecodingCoordinator().retrieve_and_decode(
        record.memory_record_id,
        SQLiteMemoryRetriever(database_path),
    )

    database_path.unlink()

    verification = MemoryRetrievalVerifier(
        SQLiteDurableMemoryEvidenceReader(database_path)
    ).verify(decoding)

    assert verification.state is VerificationState.UNKNOWN
    assert verification.decoding is decoding
