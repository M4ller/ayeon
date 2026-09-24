"""Offline test for selecting Gemini in Ayeon's text console."""

from ayeon.demo_chat import main


def test_chat_can_use_injected_gemini_generator(monkeypatch, capsys) -> None:
    class FakeGenerator:
        def generate(self, prompt: str) -> str:
            assert prompt == "hola"
            return "Respuesta simulada de Gemini."

    messages = iter(["hola", "salir"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(messages))
    monkeypatch.setenv("AYEON_USE_GEMINI", "1")
    monkeypatch.delenv("AYEON_USE_OPENAI", raising=False)
    monkeypatch.setattr(
        "ayeon.demo_chat.GeminiGenerator",
        lambda: FakeGenerator(),
    )

    main()

    assert "Respuesta simulada de Gemini." in capsys.readouterr().out
