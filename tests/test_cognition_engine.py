from ayeon.contracts.cognition import CognitiveOutput
from ayeon.contracts.cognitive_context import CognitiveContext
from ayeon.contracts.common import HealthState, TraceContext
from ayeon.contracts.state import AyeonStateSnapshot
from ayeon.core.cognition.engine import CognitionEngine


class FakeCognitionEngine:
    def process(
        self,
        context: CognitiveContext,
    ) -> CognitiveOutput:
        return CognitiveOutput(
            trace=context.trace,
            spoken_response="Entendido.",
        )


def make_context() -> CognitiveContext:
    return CognitiveContext(
        trace=TraceContext.root(),
        user_input="Hola Ayeon",
        state_snapshot=AyeonStateSnapshot(
            sequence=1,
            runtime_health=HealthState.HEALTHY,
            domains={},
        ),
    )


def test_cognition_engine_accepts_structural_implementation() -> None:
    engine: CognitionEngine = FakeCognitionEngine()

    assert isinstance(engine, CognitionEngine)


def test_cognition_engine_processes_context_into_output() -> None:
    engine: CognitionEngine = FakeCognitionEngine()
    context = make_context()

    output = engine.process(context)

    assert isinstance(output, CognitiveOutput)
    assert output.trace is context.trace
    assert output.spoken_response == "Entendido."

class NotACognitionEngine:
    pass


def test_cognition_engine_rejects_missing_process_method() -> None:
    candidate = NotACognitionEngine()

    assert not isinstance(candidate, CognitionEngine)


def test_cognition_engine_requires_no_inheritance() -> None:
    candidate = FakeCognitionEngine()

    assert isinstance(candidate, CognitionEngine)
    assert CognitionEngine not in type(candidate).__bases__