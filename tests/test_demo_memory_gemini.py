"""Offline test for verified memory reaching Gemini in one session."""

from ayeon.demo_memory import main


def test_verified_relevant_memory_reaches_gemini(monkeypatch, capsys) -> None:
    prompts = []

    class FakeGenerator:
        def generate(self, prompt: str) -> str:
            prompts.append(prompt)
            return "Te gusta el café."

    messages = iter([
        "guardar: me gusta el café",
        "¿qué me gusta?",
        "recordar: té",
        "salir",
    ])
    monkeypatch.setattr("builtins.input", lambda prompt: next(messages))
    monkeypatch.setenv("AYEON_USE_GEMINI", "1")
    monkeypatch.setattr(
        "ayeon.demo_memory.GeminiGenerator",
        lambda: FakeGenerator(),
        raising=False,
    )

    main()

    output = capsys.readouterr().out
    assert "Guardé ese dato" in output
    assert "Te gusta el café." in output
    assert "No encontré un recuerdo verificado" in output
    assert len(prompts) == 1
    assert "¿qué me gusta?" in prompts[0]
    assert "me gusta el café" in prompts[0]
