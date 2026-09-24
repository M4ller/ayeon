"""Tests for the console demo cognition engine."""

from ayeon.contracts.common import HealthState, TraceContext
from ayeon.contracts.state import AyeonStateSnapshot
from ayeon.core.cognition.coordinator import CognitionCoordinator
from ayeon.core.context.builder import ContextBuilder
from ayeon.demo_cognition import DemoCognitionEngine


def test_demo_engine_responds_through_cognition_coordinator() -> None:
    trace = TraceContext.root()
    coordinator = CognitionCoordinator(
        context_builder=ContextBuilder(),
        cognition_engine=DemoCognitionEngine(),
    )

    output = coordinator.process(
        trace=trace,
        user_input="hola",
        state_snapshot=AyeonStateSnapshot(
            sequence=0,
            runtime_health=HealthState.HEALTHY,
        ),
    )

    assert output.trace is trace
    assert output.spoken_response is not None
    assert "Hola" in output.spoken_response
    assert output.action_intents == ()
    assert output.memory_intents == ()
