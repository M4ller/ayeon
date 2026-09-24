"""Tests for memory surviving separate console sessions."""

from ayeon.demo_memory import main


def test_saved_fact_survives_console_restart(tmp_path, monkeypatch, capsys) -> None:
    monkeypatch.setenv("AYEON_MEMORY_DB", str(tmp_path / "ayeon-memory.db"))
    monkeypatch.delenv("AYEON_USE_GEMINI", raising=False)

    first_session = iter(["guardar: me gusta el cafe", "salir"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(first_session))
    main()
    assert "Guardé ese dato" in capsys.readouterr().out

    second_session = iter(["recordar: cafe", "salir"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(second_session))
    main()
    assert "Recuerdo: me gusta el cafe" in capsys.readouterr().out

def test_changed_sqlite_bytes_are_not_recalled_after_restart(
    tmp_path, monkeypatch, capsys
) -> None:
    import sqlite3

    database_path = tmp_path / "ayeon-memory.db"
    monkeypatch.setenv("AYEON_MEMORY_DB", str(database_path))
    monkeypatch.delenv("AYEON_USE_GEMINI", raising=False)

    first_session = iter(["guardar: me gusta el cafe", "salir"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(first_session))
    main()
    capsys.readouterr()

    with sqlite3.connect(database_path) as connection:
        connection.execute(
            "UPDATE memory_records SET record_payload = ?",
            (b"altered payload",),
        )

    second_session = iter(["recordar: cafe", "salir"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(second_session))
    main()

    assert "No encontré un recuerdo verificado" in capsys.readouterr().out

def test_verified_memory_reaches_gemini_after_restart(
    tmp_path, monkeypatch, capsys
) -> None:
    database_path = tmp_path / "ayeon-memory.db"
    prompts = []

    class FakeGenerator:
        def generate(self, prompt: str) -> str:
            prompts.append(prompt)
            return "Te gusta el cafe."

    monkeypatch.setenv("AYEON_MEMORY_DB", str(database_path))
    monkeypatch.setenv("AYEON_USE_GEMINI", "1")
    monkeypatch.setattr(
        "ayeon.demo_memory.GeminiGenerator",
        lambda: FakeGenerator(),
    )

    first_session = iter(["guardar: me gusta el cafe", "salir"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(first_session))
    main()
    capsys.readouterr()

    second_session = iter(["que me gusta?", "salir"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(second_session))
    main()

    assert "Te gusta el cafe." in capsys.readouterr().out
    assert len(prompts) == 1
    assert "me gusta el cafe" in prompts[0]


def test_damaged_reference_is_not_recalled(
    tmp_path, monkeypatch, capsys
) -> None:
    database_path = tmp_path / "ayeon-memory.db"
    monkeypatch.setenv("AYEON_MEMORY_DB", str(database_path))
    monkeypatch.delenv("AYEON_USE_GEMINI", raising=False)

    first_session = iter(["guardar: me gusta el cafe", "salir"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(first_session))
    main()
    capsys.readouterr()

    database_path.with_suffix(".references.jsonl").write_bytes(b"damaged\n")

    second_session = iter(["recordar: cafe", "salir"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(second_session))
    main()

    assert "No encontré un recuerdo verificado" in capsys.readouterr().out
