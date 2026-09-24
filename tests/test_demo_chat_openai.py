"""Offline tests for selecting OpenAI in the text console."""

from ayeon.demo_chat import main


def test_chat_can_use_injected_openai_generator(monkeypatch, capsys) -> None:
    class FakeGenerator:
        def generate(self, prompt: str) -> str:
            assert prompt == "hola"
            return "Respuesta simulada de Ayeon."

    messages = iter(["hola", "salir"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(messages))
    monkeypatch.setenv("AYEON_USE_OPENAI", "1")
    monkeypatch.setattr(
        "ayeon.demo_chat.OpenAIResponsesGenerator",
        lambda: FakeGenerator(),
    )

    main()

    assert "Respuesta simulada de Ayeon." in capsys.readouterr().out
