import sqlite3

from ayeon.contracts.common import ResultState, TraceContext
from ayeon.contracts.memory import (
    AdmittedMemoryIntent,
    MemoryAdmissionDecision,
    MemoryAdmissionOutcome,
    MemoryIntent,
    MemoryRecord,
)
from ayeon.contracts.verification import VerificationState
from ayeon.memory.deterministic_persistence_verifier import (
    DeterministicMemoryPersistenceVerifier,
)
from ayeon.memory.sqlite_evidence_reader import (
    SQLiteDurableMemoryEvidenceReader,
)
from ayeon.memory.sqlite_repository import SQLiteMemoryRepository


def make_record() -> MemoryRecord:
    trace = TraceContext.root()
    intent = MemoryIntent(
        content={"fact": "integration test"},
        proposed_by="test",
        trace=trace,
        reason="Integration test memory.",
    )
    admission = MemoryAdmissionDecision(
        memory_intent_id=intent.memory_intent_id,
        outcome=MemoryAdmissionOutcome.ACCEPT,
        decided_by="test",
        trace=trace,
        reason="Accepted for integration test.",
    )
    return MemoryRecord.from_admitted(
        AdmittedMemoryIntent(
            intent=intent,
            admission=admission,
        )
    )


def test_sqlite_persistence_can_be_independently_verified(
    tmp_path,
) -> None:
    database_path = tmp_path / "memory.db"
    repository = SQLiteMemoryRepository(database_path)
    record = make_record()

    persistence = repository.store(record)

    assert persistence.state is ResultState.SUCCESS

    reader = SQLiteDurableMemoryEvidenceReader(database_path)
    verifier = DeterministicMemoryPersistenceVerifier(reader)

    verification = verifier.verify(record, persistence)

    assert verification.state is VerificationState.VERIFIED
    assert verification.memory_record_id == record.memory_record_id
    assert verification.repository_name == repository.name


def test_sqlite_verification_detects_tampered_durable_payload(
    tmp_path,
) -> None:
    database_path = tmp_path / "memory.db"
    repository = SQLiteMemoryRepository(database_path)
    record = make_record()

    persistence = repository.store(record)

    assert persistence.state is ResultState.SUCCESS

    with sqlite3.connect(database_path) as connection:
        connection.execute(
            """
            UPDATE memory_records
            SET record_payload = ?
            WHERE memory_record_id = ?
            """,
            (
                b'{"tampered":true}',
                str(record.memory_record_id),
            ),
        )

    reader = SQLiteDurableMemoryEvidenceReader(database_path)
    verifier = DeterministicMemoryPersistenceVerifier(reader)

    verification = verifier.verify(record, persistence)

    assert verification.state is VerificationState.FAILED
    assert "does not match" in verification.reason.lower()

def test_sqlite_verification_reports_unknown_when_storage_is_unavailable(
    tmp_path,
) -> None:
    database_path = tmp_path / "memory.db"
    repository = SQLiteMemoryRepository(database_path)
    record = make_record()

    persistence = repository.store(record)

    assert persistence.state is ResultState.SUCCESS
    assert database_path.exists()

    database_path.unlink()

    reader = SQLiteDurableMemoryEvidenceReader(database_path)
    verifier = DeterministicMemoryPersistenceVerifier(reader)

    verification = verifier.verify(record, persistence)

    assert verification.state is VerificationState.UNKNOWN
    assert "could not be determined" in verification.reason.lower()
    assert not database_path.exists()
