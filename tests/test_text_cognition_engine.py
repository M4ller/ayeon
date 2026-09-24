"""Tests for a text generator behind Ayeon's cognition boundary."""

from ayeon.contracts.common import HealthState, TraceContext
from ayeon.contracts.state import AyeonStateSnapshot
from ayeon.core.cognition.coordinator import CognitionCoordinator
from ayeon.core.cognition.text_engine import TextCognitionEngine
from ayeon.core.context.builder import ContextBuilder


def test_generated_text_has_no_action_capability() -> None:
    prompts = []

    class FakeGenerator:
        def generate(self, prompt: str) -> str:
            prompts.append(prompt)
            return "Estoy bien, gracias por preguntar."

    trace = TraceContext.root()
    coordinator = CognitionCoordinator(
        context_builder=ContextBuilder(),
        cognition_engine=TextCognitionEngine(FakeGenerator()),
    )

    output = coordinator.process(
        trace=trace,
        user_input="¿Cómo estás?",
        state_snapshot=AyeonStateSnapshot(
            sequence=1,
            runtime_health=HealthState.HEALTHY,
        ),
    )

    assert prompts == ["¿Cómo estás?"]
    assert output.trace is trace
    assert output.spoken_response == "Estoy bien, gracias por preguntar."
    assert output.action_intents == ()
    assert output.memory_intents == ()

def test_text_engine_rejects_blank_generator_response() -> None:
    import pytest

    class BlankGenerator:
        def generate(self, prompt: str) -> str:
            return "   "

    coordinator = CognitionCoordinator(
        context_builder=ContextBuilder(),
        cognition_engine=TextCognitionEngine(BlankGenerator()),
    )

    with pytest.raises(ValueError, match="non-blank"):
        coordinator.process(
            trace=TraceContext.root(),
            user_input="Hola",
            state_snapshot=AyeonStateSnapshot(
                sequence=1,
                runtime_health=HealthState.HEALTHY,
            ),
        )
