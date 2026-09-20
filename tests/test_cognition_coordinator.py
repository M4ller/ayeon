"""Tests for cognition coordination."""

from ayeon.contracts.cognition import CognitiveOutput
from ayeon.contracts.common import HealthState, TraceContext
from ayeon.contracts.runtime_state import RuntimeStateView
from ayeon.core.cognition.coordinator import CognitionCoordinator
from ayeon.core.context.builder import ContextBuilder
from ayeon.runtime.snapshot_builder import StateSnapshotBuilder


class FakeCognitionEngine:
    """Record the context received and return a deterministic output."""

    def __init__(self) -> None:
        self.received_context = None
        self.produced_output = None

    def process(self, context):
        self.received_context = context
        self.produced_output = CognitiveOutput(
            trace=context.trace,
            spoken_response="Entendido.",
        )
        return self.produced_output


def make_runtime_state() -> RuntimeStateView:
    return RuntimeStateView(
        lifecycle="RUNNING",
        health=HealthState.HEALTHY,
        health_reports=(),
        has_critical_failure=False,
    )


def test_coordinator_builds_context_and_processes_it() -> None:
    trace = TraceContext.root()
    snapshot = StateSnapshotBuilder().build(
        runtime=make_runtime_state()
    )
    engine = FakeCognitionEngine()
    coordinator = CognitionCoordinator(
        context_builder=ContextBuilder(),
        cognition_engine=engine,
    )

    output = coordinator.process(
        trace=trace,
        user_input="Continúa.",
        state_snapshot=snapshot,
    )

    assert engine.received_context is not None
    assert engine.received_context.trace == trace
    assert engine.received_context.user_input == "Continúa."
    assert engine.received_context.state_snapshot == snapshot
    assert output.spoken_response == "Entendido."
    assert output.trace == trace


def test_coordinator_returns_engine_output_unchanged() -> None:
    trace = TraceContext.root()
    snapshot = StateSnapshotBuilder().build(
        runtime=make_runtime_state()
    )
    engine = FakeCognitionEngine()
    coordinator = CognitionCoordinator(
        context_builder=ContextBuilder(),
        cognition_engine=engine,
    )

    output = coordinator.process(
        trace=trace,
        user_input="Analiza esto.",
        state_snapshot=snapshot,
    )

    assert output is engine.produced_output
