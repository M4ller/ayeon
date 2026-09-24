"""Offline tests for Ayeon's OpenAI Responses adapter."""

from types import SimpleNamespace

from ayeon.openai_generator import OpenAIResponsesGenerator


def test_openai_generator_uses_responses_api_without_storing_response() -> None:
    calls = []

    class FakeResponses:
        def create(self, **kwargs):
            calls.append(kwargs)
            return SimpleNamespace(output_text="Hola, Felipe.")

    client = SimpleNamespace(responses=FakeResponses())
    generator = OpenAIResponsesGenerator(
        client=client,
        model="gpt-6-astra",
    )

    text = generator.generate("¿Cómo estás?")

    assert text == "Hola, Felipe."
    assert calls[0]["model"] == "gpt-6-astra"
    assert calls[0]["input"] == "¿Cómo estás?"
    assert calls[0]["store"] is False
    assert "Ayeon" in calls[0]["instructions"]
