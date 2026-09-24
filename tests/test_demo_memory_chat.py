"""Tests for the combined memory and text console demo."""

from ayeon.demo_memory import main


def test_one_session_can_remember_and_respond(monkeypatch, capsys) -> None:
    messages = iter(
        [
            "guardar: me gusta el café",
            "recordar: café",
            "hola",
            "salir",
        ]
    )
    monkeypatch.setattr("builtins.input", lambda prompt: next(messages))

    main()

    output = capsys.readouterr().out
    assert "Guardé ese dato" in output
    assert "Recuerdo: me gusta el café" in output
    assert "Hola. Soy la demo de texto de Ayeon." in output

def test_empty_recall_request_asks_for_a_word(monkeypatch, capsys) -> None:
    messages = iter(["recordar:   ", "salir"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(messages))

    main()

    output = capsys.readouterr().out
    assert "Escribe una palabra después de recordar:" in output
