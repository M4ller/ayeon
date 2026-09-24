"""Tests for memory context eligibility."""

from test_sqlite_memory_repository import make_record

from ayeon.contracts.memory_context_eligibility import (
    MemoryContextEligibilityOutcome,
)
from ayeon.memory.context_eligibility import MemoryContextEligibilityPolicy
from ayeon.memory.deterministic_persistence_verifier import (
    DeterministicMemoryPersistenceVerifier,
)
from ayeon.memory.retrieval_decoding_coordinator import (
    MemoryRetrievalDecodingCoordinator,
)
from ayeon.memory.retrieval_verifier import MemoryRetrievalVerifier
from ayeon.memory.sqlite_evidence_reader import SQLiteDurableMemoryEvidenceReader
from ayeon.memory.sqlite_repository import SQLiteMemoryRepository
from ayeon.memory.sqlite_retriever import SQLiteMemoryRetriever


def test_verified_original_record_is_eligible(tmp_path) -> None:
    database_path = tmp_path / "memory.db"
    record = make_record()
    persistence = SQLiteMemoryRepository(database_path).store(record)
    reader = SQLiteDurableMemoryEvidenceReader(database_path)

    decoding = MemoryRetrievalDecodingCoordinator().retrieve_and_decode(
        record.memory_record_id,
        SQLiteMemoryRetriever(database_path),
    )
    retrieval_verification = MemoryRetrievalVerifier(reader).verify(decoding)
    persistence_verification = DeterministicMemoryPersistenceVerifier(
        reader
    ).verify(record, persistence)

    decision = MemoryContextEligibilityPolicy().evaluate(
        record=record,
        retrieval_verification=retrieval_verification,
        persistence_verification=persistence_verification,
    )

    assert decision.outcome is MemoryContextEligibilityOutcome.ELIGIBLE
    assert decision.memory_record_id == record.memory_record_id

def test_decodable_changed_record_is_ineligible(tmp_path) -> None:
    import sqlite3
    from datetime import timedelta

    from ayeon.contracts.memory import MemoryRecord
    from ayeon.contracts.verification import VerificationState
    from ayeon.memory.serialization import encode_memory_record

    database_path = tmp_path / "memory.db"
    record = make_record()
    persistence = SQLiteMemoryRepository(database_path).store(record)

    altered = MemoryRecord(
        admitted=record.admitted,
        memory_record_id=record.memory_record_id,
        created_at=record.created_at + timedelta(seconds=1),
    )
    with sqlite3.connect(database_path) as connection:
        connection.execute(
            """
            UPDATE memory_records
            SET record_payload = ?
            WHERE memory_record_id = ?
            """,
            (encode_memory_record(altered), str(record.memory_record_id)),
        )

    reader = SQLiteDurableMemoryEvidenceReader(database_path)
    decoding = MemoryRetrievalDecodingCoordinator().retrieve_and_decode(
        record.memory_record_id,
        SQLiteMemoryRetriever(database_path),
    )
    retrieval_verification = MemoryRetrievalVerifier(reader).verify(decoding)
    persistence_verification = DeterministicMemoryPersistenceVerifier(
        reader
    ).verify(record, persistence)

    decision = MemoryContextEligibilityPolicy().evaluate(
        record=record,
        retrieval_verification=retrieval_verification,
        persistence_verification=persistence_verification,
    )

    assert decoding.decoded is not None
    assert retrieval_verification.state is VerificationState.VERIFIED
    assert persistence_verification.state is VerificationState.FAILED
    assert decision.outcome is MemoryContextEligibilityOutcome.INELIGIBLE
