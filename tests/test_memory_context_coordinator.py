"""Integration tests for memory context coordination."""

from test_sqlite_memory_repository import make_record

from ayeon.contracts.memory_context_relevance import (
    MemoryContextRelevanceOutcome,
)
from ayeon.memory.context_coordinator import MemoryContextCoordinator
from ayeon.memory.deterministic_persistence_verifier import (
    DeterministicMemoryPersistenceVerifier,
)
from ayeon.memory.persistence_coordinator import MemoryPersistenceCoordinator
from ayeon.memory.persistence_verification_coordinator import (
    MemoryPersistenceVerificationCoordinator,
)
from ayeon.memory.retrieval_decoding_coordinator import (
    MemoryRetrievalDecodingCoordinator,
)
from ayeon.memory.retrieval_verifier import MemoryRetrievalVerifier
from ayeon.memory.sqlite_evidence_reader import (
    SQLiteDurableMemoryEvidenceReader,
)
from ayeon.memory.sqlite_repository import SQLiteMemoryRepository
from ayeon.memory.sqlite_retriever import SQLiteMemoryRetriever


def test_verified_relevant_memory_reaches_context(tmp_path) -> None:
    database = tmp_path / "memory.db"
    record = make_record()

    repository = SQLiteMemoryRepository(database)
    persistence = MemoryPersistenceCoordinator().persist(
        record,
        repository,
    )

    persistence_verification = (
        MemoryPersistenceVerificationCoordinator().verify(
            record,
            persistence,
            DeterministicMemoryPersistenceVerifier(SQLiteDurableMemoryEvidenceReader(database)),
        )
    )

    retriever = SQLiteMemoryRetriever(database)
    decoding = MemoryRetrievalDecodingCoordinator().retrieve_and_decode(
        record.memory_record_id,
        retriever,
    )

    retrieval_verification = MemoryRetrievalVerifier(
        SQLiteDurableMemoryEvidenceReader(database)
    ).verify(decoding)

    class RelevantEvaluator:
        def evaluate(self, user_input, decoded):
            return MemoryContextRelevanceOutcome.RELEVANT

    entry = MemoryContextCoordinator().select(
        user_input="¿Qué recuerdas?",
        record=record,
        retrieval_verification=retrieval_verification,
        persistence_verification=persistence_verification.verification,
        evaluator=RelevantEvaluator(),
    )

    assert entry is not None
    assert entry.memory_record_id == record.memory_record_id


def test_verified_irrelevant_memory_does_not_reach_context(
    tmp_path,
) -> None:
    database = tmp_path / "memory.db"
    record = make_record()

    repository = SQLiteMemoryRepository(database)
    persistence = MemoryPersistenceCoordinator().persist(
        record,
        repository,
    )

    persistence_verification = (
        MemoryPersistenceVerificationCoordinator().verify(
            record,
            persistence,
            DeterministicMemoryPersistenceVerifier(SQLiteDurableMemoryEvidenceReader(database)),
        )
    )

    decoding = MemoryRetrievalDecodingCoordinator().retrieve_and_decode(
        record.memory_record_id,
        SQLiteMemoryRetriever(database),
    )

    retrieval_verification = MemoryRetrievalVerifier(
        SQLiteDurableMemoryEvidenceReader(database)
    ).verify(decoding)

    class IrrelevantEvaluator:
        def evaluate(self, user_input, decoded):
            return MemoryContextRelevanceOutcome.IRRELEVANT

    entry = MemoryContextCoordinator().select(
        user_input="Tema no relacionado",
        record=record,
        retrieval_verification=retrieval_verification,
        persistence_verification=persistence_verification.verification,
        evaluator=IrrelevantEvaluator(),
    )

    assert entry is None
