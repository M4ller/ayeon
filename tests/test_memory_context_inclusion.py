from ayeon.contracts.memory_context_relevance import (
    MemoryContextRelevanceDecision,
    MemoryContextRelevanceOutcome,
)
from ayeon.memory.context_inclusion import MemoryContextInclusionPolicy


def make_decoded():
    from test_sqlite_memory_repository import make_record

    from ayeon.memory.decoder import decode_memory_record
    from ayeon.memory.serialization import encode_memory_record

    record = make_record()
    decoded = decode_memory_record(encode_memory_record(record))
    return record, decoded


def test_relevant_memory_becomes_context_entry() -> None:
    record, decoded = make_decoded()

    relevance = MemoryContextRelevanceDecision(
        memory_record_id=record.memory_record_id,
        outcome=MemoryContextRelevanceOutcome.RELEVANT,
        reason="Relevant to current request.",
    )

    entry = MemoryContextInclusionPolicy().include(
        relevance=relevance,
        decoded=decoded,
    )

    assert entry is not None
    assert entry.memory_record_id == record.memory_record_id
    assert entry.decoded is decoded


def test_irrelevant_memory_is_not_included() -> None:
    record, decoded = make_decoded()

    relevance = MemoryContextRelevanceDecision(
        memory_record_id=record.memory_record_id,
        outcome=MemoryContextRelevanceOutcome.IRRELEVANT,
        reason="Not relevant.",
    )

    entry = MemoryContextInclusionPolicy().include(
        relevance=relevance,
        decoded=decoded,
    )

    assert entry is None


def test_unknown_memory_is_not_included() -> None:
    record, decoded = make_decoded()

    relevance = MemoryContextRelevanceDecision(
        memory_record_id=record.memory_record_id,
        outcome=MemoryContextRelevanceOutcome.UNKNOWN,
        reason="Relevance could not be established.",
    )

    entry = MemoryContextInclusionPolicy().include(
        relevance=relevance,
        decoded=decoded,
    )

    assert entry is None


def test_relevant_memory_without_decoded_content_is_not_included() -> None:
    record, _ = make_decoded()

    relevance = MemoryContextRelevanceDecision(
        memory_record_id=record.memory_record_id,
        outcome=MemoryContextRelevanceOutcome.RELEVANT,
        reason="Relevant.",
    )

    entry = MemoryContextInclusionPolicy().include(
        relevance=relevance,
        decoded=None,
    )

    assert entry is None


def test_relevant_memory_with_mismatched_identity_is_rejected() -> None:
    import pytest

    record, _ = make_decoded()
    other_record, other_decoded = make_decoded()

    relevance = MemoryContextRelevanceDecision(
        memory_record_id=record.memory_record_id,
        outcome=MemoryContextRelevanceOutcome.RELEVANT,
        reason="Relevant.",
    )

    assert other_record.memory_record_id != record.memory_record_id

    with pytest.raises(
        ValueError,
        match="decoded memory_record_id must match relevance",
    ):
        MemoryContextInclusionPolicy().include(
            relevance=relevance,
            decoded=other_decoded,
        )