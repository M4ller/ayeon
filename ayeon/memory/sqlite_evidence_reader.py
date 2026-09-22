"""Read-only SQLite durable memory evidence for Ayeon Core."""

from __future__ import annotations

import sqlite3
from contextlib import closing
from pathlib import Path

from ayeon.contracts.common import MemoryRecordId


class SQLiteDurableMemoryEvidenceReader:
    """Read canonical durable payloads from an existing SQLite repository."""

    def __init__(self, database_path: str | Path) -> None:
        self._database_path = Path(database_path)

    @property
    def name(self) -> str:
        return "sqlite_durable_memory_evidence_reader"

    def _connect(self) -> sqlite3.Connection:
        database_uri = self._database_path.resolve().as_uri() + "?mode=ro"
        return sqlite3.connect(database_uri, uri=True)

    def read_payload(
        self,
        memory_record_id: MemoryRecordId,
    ) -> bytes | None:
        """Read one durable payload without modifying repository state."""

        with closing(self._connect()) as connection:
            schema_version = connection.execute(
                "PRAGMA user_version"
            ).fetchone()[0]

            if schema_version != 1:
                raise RuntimeError(
                    "Unsupported SQLite schema version: "
                    f"{schema_version}."
                )

            row = connection.execute(
                """
                SELECT record_payload
                FROM memory_records
                WHERE memory_record_id = ?
                """,
                (str(memory_record_id),),
            ).fetchone()

        if row is None:
            return None

        return bytes(row[0])