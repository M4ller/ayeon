"""Offline tests for Ayeon's Gemini adapter."""

from types import SimpleNamespace

import pytest

from ayeon.gemini_generator import GeminiGenerator


def test_gemini_generator_uses_model_and_instructions() -> None:
    calls = []

    class FakeModels:
        def generate_content(self, **kwargs):
            calls.append(kwargs)
            return SimpleNamespace(text="Hola, Felipe.")

    generator = GeminiGenerator(
        client=SimpleNamespace(models=FakeModels()),
        model="gemini-3.5-flash-lite",
    )

    assert generator.generate("hola") == "Hola, Felipe."
    assert calls[0]["model"] == "gemini-3.5-flash-lite"
    assert calls[0]["contents"] == "hola"
    assert "Ayeon" in calls[0]["config"].system_instruction
    assert calls[0]["config"].automatic_function_calling.disable is True


def test_gemini_generator_rejects_empty_response() -> None:
    class FakeModels:
        def generate_content(self, **kwargs):
            return SimpleNamespace(text=None)

    generator = GeminiGenerator(client=SimpleNamespace(models=FakeModels()))

    with pytest.raises(ValueError, match="did not contain text"):
        generator.generate("hola")
