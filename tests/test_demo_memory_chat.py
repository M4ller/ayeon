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

def test_natural_question_and_recall_phrase_find_saved_fact(
    monkeypatch, capsys
) -> None:
    messages = iter(
        [
            "guardar: me gusta el cafe",
            "que me gusta?",
            "recordar: que me gusta",
            "recordar: no me gusta el te",
            "salir",
        ]
    )
    monkeypatch.setattr("builtins.input", lambda prompt: next(messages))

    main()

    output = capsys.readouterr().out
    assert output.count("Recuerdo: me gusta el cafe") == 2
    assert "No encontré un recuerdo verificado" in output


def test_recall_without_colon_shows_usage(monkeypatch, capsys) -> None:
    messages = iter(["recordar", "salir"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(messages))

    main()

    assert "Escribe recordar: <palabra>" in capsys.readouterr().out
