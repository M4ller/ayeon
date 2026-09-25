from datetime import UTC, datetime

from ayeon.contracts.common import (
    CausationId,
    CorrelationId,
    MemoryIntentId,
    MemoryRecordId,
)
from ayeon.contracts.memory_context_relevance import MemoryContextRelevanceOutcome
from ayeon.contracts.memory_decoding import DecodedMemoryRecord
from ayeon.memory.lexical_relevance import LexicalMemoryRelevanceEvaluator


def _decoded_memory(fact: str) -> DecodedMemoryRecord:
    record_id = MemoryRecordId("memory-test")

    return DecodedMemoryRecord(
        memory_record_id=record_id,
        source_memory_intent_id=MemoryIntentId("intent-test"),
        created_at=datetime.now(UTC),
        correlation_id=CorrelationId("correlation-test"),
        causation_id=CausationId("causation-test"),
        content={"fact": fact},
    )


def test_matches_related_exit_concepts() -> None:
    evaluator = LexicalMemoryRelevanceEvaluator()

    outcome = evaluator.evaluate(
        "salir",
        _decoded_memory("me quiero ir"),
    )

    assert outcome is MemoryContextRelevanceOutcome.RELEVANT


def test_matches_related_coffee_concepts() -> None:
    evaluator = LexicalMemoryRelevanceEvaluator()

    outcome = evaluator.evaluate(
        "cafeteria",
        _decoded_memory("mi cafe favorito es el irlandez"),
    )

    assert outcome is MemoryContextRelevanceOutcome.RELEVANT


def test_unrelated_memory_is_not_relevant() -> None:
    evaluator = LexicalMemoryRelevanceEvaluator()

    outcome = evaluator.evaluate(
        "perro",
        _decoded_memory("mi cafe favorito es el irlandez"),
    )

    assert outcome is MemoryContextRelevanceOutcome.UNKNOWN
