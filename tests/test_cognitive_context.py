import pytest

from ayeon.contracts.cognitive_context import CognitiveContext
from ayeon.contracts.common import HealthState, TraceContext
from ayeon.contracts.state import AyeonStateSnapshot


def make_snapshot() -> AyeonStateSnapshot:
    return AyeonStateSnapshot(
        sequence=7,
        runtime_health=HealthState.HEALTHY,
        domains={},
    )


def test_cognitive_context_accepts_valid_input() -> None:
    trace = TraceContext.root()
    snapshot = make_snapshot()

    context = CognitiveContext(
        trace=trace,
        user_input="Hola Ayeon",
        state_snapshot=snapshot,
    )

    assert context.trace is trace
    assert context.user_input == "Hola Ayeon"
    assert context.state_snapshot is snapshot


def test_cognitive_context_rejects_blank_user_input() -> None:
    with pytest.raises(ValueError, match="user_input must not be blank"):
        CognitiveContext(
            trace=TraceContext.root(),
            user_input="   ",
            state_snapshot=make_snapshot(),
        )

def test_cognitive_context_rejects_empty_user_input() -> None:
    with pytest.raises(ValueError, match="user_input must not be blank"):
        CognitiveContext(
            trace=TraceContext.root(),
            user_input="",
            state_snapshot=make_snapshot(),
        )


def test_cognitive_context_is_immutable() -> None:
    context = CognitiveContext(
        trace=TraceContext.root(),
        user_input="Hola Ayeon",
        state_snapshot=make_snapshot(),
    )

    with pytest.raises(AttributeError):
        context.user_input = "modified"


def test_cognitive_context_preserves_snapshot_identity() -> None:
    snapshot = make_snapshot()

    context = CognitiveContext(
        trace=TraceContext.root(),
        user_input="Analiza tu estado",
        state_snapshot=snapshot,
    )

    assert context.state_snapshot is snapshot