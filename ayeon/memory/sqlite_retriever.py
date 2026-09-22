"""Read-only SQLite durable memory retrieval for Ayeon Core."""

from __future__ import annotations

import sqlite3
from contextlib import closing
from pathlib import Path

from ayeon.contracts.common import MemoryRecordId
from ayeon.contracts.memory_retrieval import (
    MemoryRetrievalOutcome,
    MemoryRetrievalResult,
)


class SQLiteMemoryRetriever:
    """Retrieve canonical durable memory payloads from SQLite."""

    def __init__(self, database_path: str | Path) -> None:
        self._database_path = Path(database_path)

    @property
    def name(self) -> str:
        return "sqlite_memory_retriever"

    def _connect(self) -> sqlite3.Connection:
        database_uri = self._database_path.resolve().as_uri() + "?mode=ro"
        return sqlite3.connect(database_uri, uri=True)

    def retrieve(
        self,
        memory_record_id: MemoryRecordId,
    ) -> MemoryRetrievalResult:
        """Retrieve one durable payload without modifying storage."""

        try:
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
        except Exception as exc:
            return MemoryRetrievalResult(
                memory_record_id=memory_record_id,
                outcome=MemoryRetrievalOutcome.UNKNOWN,
                retrieved_by=self.name,
                payload=None,
                reason=(
                    "Durable memory retrieval could not determine "
                    "storage state: "
                    f"{type(exc).__name__}"
                ),
            )

        if row is None:
            return MemoryRetrievalResult(
                memory_record_id=memory_record_id,
                outcome=MemoryRetrievalOutcome.NOT_FOUND,
                retrieved_by=self.name,
                payload=None,
                reason="Durable memory record was not found.",
            )

        return MemoryRetrievalResult(
            memory_record_id=memory_record_id,
            outcome=MemoryRetrievalOutcome.FOUND,
            retrieved_by=self.name,
            payload=bytes(row[0]),
            reason="Durable memory payload was found.",
        )