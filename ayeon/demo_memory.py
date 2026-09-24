"""Interactive, session-only demonstration of Ayeon's memory pipeline."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from ayeon.contracts.common import HealthState, ResultState, TraceContext
from ayeon.contracts.memory import (
    AdmittedMemoryIntent,
    MemoryAdmissionDecision,
    MemoryAdmissionOutcome,
    MemoryIntent,
    MemoryRecord,
)
from ayeon.contracts.memory_context_eligibility import (
    MemoryContextEligibilityOutcome,
)
from ayeon.contracts.memory_context_relevance import (
    MemoryContextRelevanceOutcome,
)
from ayeon.contracts.state import AyeonStateSnapshot
from ayeon.core.cognition.coordinator import CognitionCoordinator
from ayeon.core.context.builder import ContextBuilder
from ayeon.demo_cognition import DemoCognitionEngine
from ayeon.memory.context_eligibility import MemoryContextEligibilityPolicy
from ayeon.memory.context_relevance import MemoryContextRelevanceCoordinator
from ayeon.memory.deterministic_persistence_verifier import (
    DeterministicMemoryPersistenceVerifier,
)
from ayeon.memory.retrieval_decoding_coordinator import (
    MemoryRetrievalDecodingCoordinator,
)
from ayeon.memory.retrieval_verifier import MemoryRetrievalVerifier
from ayeon.memory.sqlite_evidence_reader import SQLiteDurableMemoryEvidenceReader
from ayeon.memory.sqlite_repository import SQLiteMemoryRepository
from ayeon.memory.sqlite_retriever import SQLiteMemoryRetriever


class KeywordEvaluator:
    """Small demo evaluator; uncertain matches remain UNKNOWN."""

    def evaluate(self, user_input, decoded):
        fact = decoded.content.get("fact")
        if not isinstance(fact, str):
            return MemoryContextRelevanceOutcome.UNKNOWN

        words = user_input.casefold().split()
        if words and all(word in fact.casefold() for word in words):
            return MemoryContextRelevanceOutcome.RELEVANT
        return MemoryContextRelevanceOutcome.UNKNOWN


def main() -> None:
    with TemporaryDirectory() as directory:
        database_path = Path(directory) / "memory.db"
        repository = SQLiteMemoryRepository(database_path)
        reader = SQLiteDurableMemoryEvidenceReader(database_path)
        saved = []
        coordinator = CognitionCoordinator(
            context_builder=ContextBuilder(),
            cognition_engine=DemoCognitionEngine(),
        )
        sequence = 0

        print("Ayeon · demo de memoria (solo durante esta sesión)")
        print("Comandos: guardar: <dato> | recordar: <palabra> | salir")

        while True:
            command = input("\nTú> ").strip()
            action, separator, value = command.partition(":")
            action = action.strip().casefold()
            value = value.strip()

            if command.casefold() == "salir":
                break

            if action == "guardar" and separator and value:
                trace = TraceContext.root()
                intent = MemoryIntent(
                    content={"fact": value},
                    proposed_by="console_demo",
                    trace=trace,
                    reason="Dato proporcionado durante la demo.",
                )
                admission = MemoryAdmissionDecision(
                    memory_intent_id=intent.memory_intent_id,
                    outcome=MemoryAdmissionOutcome.ACCEPT,
                    decided_by="console_demo",
                    trace=trace,
                    reason="Ingreso explícito del usuario en la demo.",
                )
                record = MemoryRecord.from_admitted(
                    AdmittedMemoryIntent(intent=intent, admission=admission)
                )
                persistence = repository.store(record)
                if persistence.state is ResultState.SUCCESS:
                    saved.append((record, persistence))
                    print("Ayeon> Guardé ese dato para esta sesión.")
                else:
                    print("Ayeon> No pude guardar ese dato.")
                continue

            if action == "recordar" and separator and not value:
                print("Ayeon> Escribe una palabra después de recordar:")
                continue
            if action == "recordar" and separator and value:
                matches = []
                for record, persistence in saved:
                    decoding = MemoryRetrievalDecodingCoordinator().retrieve_and_decode(
                        record.memory_record_id,
                        SQLiteMemoryRetriever(database_path),
                    )
                    retrieval_check = MemoryRetrievalVerifier(reader).verify(decoding)
                    persistence_check = DeterministicMemoryPersistenceVerifier(
                        reader
                    ).verify(record, persistence)
                    eligibility = MemoryContextEligibilityPolicy().evaluate(
                        record=record,
                        retrieval_verification=retrieval_check,
                        persistence_verification=persistence_check,
                    )
                    if eligibility.outcome is not MemoryContextEligibilityOutcome.ELIGIBLE:
                        continue

                    relevance = MemoryContextRelevanceCoordinator().evaluate(
                        user_input=value,
                        eligibility=eligibility,
                        decoded=decoding.decoded,
                        evaluator=KeywordEvaluator(),
                    )
                    if relevance.outcome is MemoryContextRelevanceOutcome.RELEVANT:
                        matches.append(record.content["fact"])

                if matches:
                    for fact in matches:
                        print(f"Ayeon> Recuerdo: {fact}")
                else:
                    print("Ayeon> No encontré un recuerdo verificado con esa palabra.")
                continue

            sequence += 1
            output = coordinator.process(
                trace=TraceContext.root(),
                user_input=command,
                state_snapshot=AyeonStateSnapshot(
                    sequence=sequence,
                    runtime_health=HealthState.HEALTHY,
                ),
            )
            print(f"Ayeon> {output.spoken_response}")


if __name__ == "__main__":
    main()
