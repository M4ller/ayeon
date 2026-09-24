"""Tests for listing and forgetting one verified memory."""

import json
import sqlite3

from ayeon.demo_memory import main


def test_forget_exact_record_preserves_other_across_restart(
    tmp_path, monkeypatch, capsys
) -> None:
    database = tmp_path / "memory.db"
    monkeypatch.setenv("AYEON_MEMORY_DB", str(database))
    monkeypatch.setenv("AYEON_USE_GEMINI", "0")

    first = iter([
        "guardar: me gusta el cafe",
        "guardar: me gusta el jugo de naranja",
        "listar",
        "salir",
    ])
    monkeypatch.setattr("builtins.input", lambda prompt: next(first))
    main()
    listing = capsys.readouterr().out

    with sqlite3.connect(database) as connection:
        rows = connection.execute(
            "SELECT memory_record_id, record_payload FROM memory_records"
        ).fetchall()

    facts = {
        json.loads(bytes(payload))["content"]["fact"]: record_id
        for record_id, payload in rows
    }
    cafe_id = facts["me gusta el cafe"]
    orange_id = facts["me gusta el jugo de naranja"]
    assert cafe_id in listing
    assert orange_id in listing

    second = iter([f"olvidar: {cafe_id}", "salir"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(second))
    main()
    assert "Recuerdo eliminado." in capsys.readouterr().out

    third = iter(["recordar: cafe", "recordar: naranja", "salir"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(third))
    main()
    output = capsys.readouterr().out

    assert "No encontré un recuerdo verificado" in output
    assert "Recuerdo: me gusta el jugo de naranja" in output
    with sqlite3.connect(database) as connection:
        remaining = connection.execute(
            "SELECT memory_record_id FROM memory_records"
        ).fetchall()
    assert remaining == [(orange_id,)]


def test_forget_unknown_id_preserves_record(tmp_path, monkeypatch, capsys) -> None:
    from uuid import uuid4

    database = tmp_path / "memory.db"
    monkeypatch.setenv("AYEON_MEMORY_DB", str(database))
    monkeypatch.setenv("AYEON_USE_GEMINI", "0")

    messages = iter([
        "guardar: me gusta el cafe",
        f"olvidar: {uuid4()}",
        "recordar: cafe",
        "salir",
    ])
    monkeypatch.setattr("builtins.input", lambda prompt: next(messages))

    main()

    output = capsys.readouterr().out
    assert "No encontre ese recuerdo." in output
    assert "Recuerdo: me gusta el cafe" in output


def test_forget_rejects_altered_record(tmp_path, monkeypatch, capsys) -> None:
    import sqlite3

    database = tmp_path / "memory.db"
    monkeypatch.setenv("AYEON_MEMORY_DB", str(database))
    monkeypatch.setenv("AYEON_USE_GEMINI", "0")

    messages = iter(["guardar: me gusta el cafe", "salir"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(messages))
    main()
    capsys.readouterr()

    with sqlite3.connect(database) as connection:
        record_id = connection.execute(
            "SELECT memory_record_id FROM memory_records"
        ).fetchone()[0]
        connection.execute(
            "UPDATE memory_records SET record_payload = ? "
            "WHERE memory_record_id = ?",
            (b"altered", record_id),
        )

    messages = iter([f"olvidar: {record_id}", "salir"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(messages))
    main()

    assert "No pude verificar ese recuerdo." in capsys.readouterr().out
    with sqlite3.connect(database) as connection:
        assert connection.execute(
            "SELECT record_payload FROM memory_records "
            "WHERE memory_record_id = ?",
            (record_id,),
        ).fetchone()[0] == b"altered"
