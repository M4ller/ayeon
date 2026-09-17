import pytest

from ayeon.contracts.cognitive_context import CognitiveContext
from ayeon.contracts.common import HealthState, TraceContext
from ayeon.contracts.state import AyeonStateSnapshot
from ayeon.core.context.builder import ContextBuilder


def make_snapshot() -> AyeonStateSnapshot:
    return AyeonStateSnapshot(
        sequence=11,
        runtime_health=HealthState.HEALTHY,
        domains={},
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