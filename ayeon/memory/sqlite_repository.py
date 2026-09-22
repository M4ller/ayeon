"""SQLite durable memory repository for Ayeon Core."""

from __future__ import annotations

import sqlite3
from contextlib import closing
from pathlib import Path

from ayeon.contracts.common import ResultState
from ayeon.contracts.memory import MemoryRecord
from ayeon.contracts.memory_persistence import MemoryPersistenceResult
from ayeon.memory.serialization import encode_memory_record


class SQLiteMemoryRepository:
    """Persist canonical memory records in a local SQLite database."""

    def __init__(self, database_path: str | Path) -> None:
        self._database_path = Path(database_path)
        self._initialize_schema()

    @property
    def name(self) -> str:
        return "sqlite_memory_repository"

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._database_path)
        connection.execute("PRAGMA synchronous = FULL")
        return connection

    def _initialize_schema(self) -> None:
        with closing(self._connect()) as connection:
            with connection:
                journal_mode = connection.execute(
                    "PRAGMA journal_mode = DELETE"
                ).fetchone()[0]

                if journal_mode.lower() != "delete":
                    raise RuntimeError(
                        "SQLite journal_mode DELETE could not be enforced."
                    )

                schema_version = connection.execute(
                    "PRAGMA user_version"
                ).fetchone()[0]

                if schema_version not in (0, 1):
                    raise RuntimeError(
                        f"Unsupported SQLite schema version: {schema_version}."
                    )

                if schema_version == 0:
                    connection.execute("BEGIN IMMEDIATE")

                connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS memory_records (
                        memory_record_id TEXT PRIMARY KEY,
                        record_payload BLOB NOT NULL
                    )
                    """
                )

                if schema_version == 0:
                    connection.execute("PRAGMA user_version = 1")

    def store(self, record: MemoryRecord) -> MemoryPersistenceResult:
        """Persist one record with identity-safe idempotency."""

        payload = encode_memory_record(record)
        record_id = str(record.memory_record_id)

        with closing(self._connect()) as connection:
            with connection:
                connection.execute("BEGIN IMMEDIATE")

                existing = connection.execute(
                    """
                    SELECT record_payload
                    FROM memory_records
                    WHERE memory_record_id = ?
                    """,
                    (record_id,),
                ).fetchone()

                if existing is not None:
                    existing_payload = bytes(existing[0])

                    if existing_payload == payload:
                        return MemoryPersistenceResult(
                            memory_record_id=record.memory_record_id,
                            repository_name=self.name,
                            state=ResultState.SUCCESS,
                            trace=record.trace,
                            summary=(
                                "Memory record already stored identically."
                            ),
                        )

                    return MemoryPersistenceResult(
                        memory_record_id=record.memory_record_id,
                        repository_name=self.name,
                        state=ResultState.FAILED,
                        trace=record.trace,
                        summary=(
                            "Memory record identity conflicts with stored payload."
                        ),
                    )

                connection.execute(
                    """
                    INSERT INTO memory_records (
                        memory_record_id,
                        record_payload
                    )
                    VALUES (?, ?)
                    """,
                    (record_id, payload),
                )

        return MemoryPersistenceResult(
            memory_record_id=record.memory_record_id,
            repository_name=self.name,
            state=ResultState.SUCCESS,
            trace=record.trace,
            summary="Memory record stored durably.",
        )
