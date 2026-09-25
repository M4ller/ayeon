from datetime import UTC, datetime

import pytest

from ayeon.contracts.cognitive_context import CognitiveContext
from ayeon.contracts.common import (
    CausationId,
    CorrelationId,
    HealthState,
    MemoryIntentId,
    MemoryRecordId,
    TraceContext,
)
from ayeon.contracts.memory_context_entry import MemoryContextEntry
from ayeon.contracts.memory_decoding import DecodedMemoryRecord
from ayeon.contracts.state import AyeonStateSnapshot
from ayeon.core.context.builder import ContextBuilder


def make_snapshot() -> AyeonStateSnapshot:
    return AyeonStateSnapshot(
        sequence=11,
        runtime_health=HealthState.HEALTHY,
        domains={},
    )


def make_memory_entry() -> MemoryContextEntry:
    record_id = MemoryRecordId("memory-1")

    decoded = DecodedMemoryRecord(
        memory_record_id=record_id,
        source_memory_intent_id=MemoryIntentId("intent-1"),
        created_at=datetime.now(UTC),
        correlation_id=CorrelationId("correlation-1"),
        causation_id=CausationId("causation-1"),
        content={"fact": "Ayeon remembers this."},
    )

    return MemoryContextEntry(
        memory_record_id=record_id,
        decoded=decoded,
    )


def test_context_builder_builds_cognitive_context() -> None:
    builder = ContextBuilder()
    trace = TraceContext.root()
    snapshot = make_snapshot()

    context = builder.build(
        trace=trace,
        user_input="Hola Ayeon",
        state_snapshot=snapshot,
    )

    assert isinstance(context, CognitiveContext)
    assert context.trace is trace
    assert context.user_input == "Hola Ayeon"
    assert context.state_snapshot is snapshot


def test_context_builder_preserves_validation_boundary() -> None:
    builder = ContextBuilder()

    with pytest.raises(ValueError, match="user_input must not be blank"):
        builder.build(
            trace=TraceContext.root(),
            user_input="   ",
            state_snapshot=make_snapshot(),
        )


def test_context_builder_preserves_trace_identity() -> None:
    builder = ContextBuilder()
    trace = TraceContext.root()

    context = builder.build(
        trace=trace,
        user_input="Continúa",
        state_snapshot=make_snapshot(),
    )

    assert context.trace is trace


def test_context_builder_preserves_snapshot_identity() -> None:
    builder = ContextBuilder()
    snapshot = make_snapshot()

    context = builder.build(
        trace=TraceContext.root(),
        user_input="Revisa tu estado",
        state_snapshot=snapshot,
    )

    assert context.state_snapshot is snapshot


def test_context_builder_does_not_mutate_snapshot() -> None:
    builder = ContextBuilder()
    snapshot = make_snapshot()

    first = builder.build(
        trace=TraceContext.root(),
        user_input="Primero",
        state_snapshot=snapshot,
    )

    second = builder.build(
        trace=TraceContext.root(),
        user_input="Segundo",
        state_snapshot=snapshot,
    )

    assert first.state_snapshot is snapshot
    assert second.state_snapshot is snapshot
    assert snapshot.sequence == 11
    assert snapshot.domains == {}


def test_context_builder_includes_memories() -> None:
    builder = ContextBuilder()
    memory = make_memory_entry()

    context = builder.build(
        trace=TraceContext.root(),
        user_input="Recuerda esto",
        state_snapshot=make_snapshot(),
        memories=(memory,),
    )

    assert context.memories == (memory,)


def test_cognitive_context_normalizes_memories_to_tuple() -> None:
    builder = ContextBuilder()
    memory = make_memory_entry()

    context = builder.build(
        trace=TraceContext.root(),
        user_input="Usa memoria",
        state_snapshot=make_snapshot(),
        memories=[memory],
    )

    assert isinstance(context.memories, tuple)
    assert context.memories == (memory,)


def test_cognitive_context_rejects_invalid_memory_entries() -> None:
    builder = ContextBuilder()

    with pytest.raises(
        TypeError,
        match="memories must contain only MemoryContextEntry",
    ):
        builder.build(
            trace=TraceContext.root(),
            user_input="Usa memoria",
            state_snapshot=make_snapshot(),
            memories=("invalid",),
        )