"""Tests for the recuerda command in the memory console."""

from ayeon.demo_memory import main


def test_recuerda_requests_a_word_and_accepts_a_query(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.setenv("AYEON_MEMORY_DB", str(tmp_path / "memory.db"))
    monkeypatch.setenv("AYEON_USE_GEMINI", "0")
    messages = iter([
        "guardar: me gusta el jugo de naranja",
        "recuerda",
        "recuerda naranja",
        "salir",
    ])
    monkeypatch.setattr("builtins.input", lambda prompt: next(messages))

    main()

    output = capsys.readouterr().out
    assert "Escribe recordar: <palabra>" in output
    assert "Recuerdo: me gusta el jugo de naranja" in output
