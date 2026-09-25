"""Interactive, session-only demonstration of Ayeon's memory pipeline."""

from __future__ import annotations

import os
from contextlib import ExitStack
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
from ayeon.contracts.memory_persistence import MemoryPersistenceResult
from ayeon.contracts.state import AyeonStateSnapshot
from ayeon.core.cognition.coordinator import CognitionCoordinator
from ayeon.core.cognition.text_engine import TextCognitionEngine
from ayeon.core.context.builder import ContextBuilder
from ayeon.demo_cognition import DemoCognitionEngine
from ayeon.gemini_generator import GeminiGenerator
from ayeon.memory.context_eligibility import MemoryContextEligibilityPolicy
from ayeon.memory.context_relevance import MemoryContextRelevanceCoordinator
from ayeon.memory.deterministic_persistence_verifier import (
    DeterministicMemoryPersistenceVerifier,
)
from ayeon.memory.lexical_relevance import LexicalMemoryRelevanceEvaluator
from ayeon.memory.record_reference_store import LocalMemoryReferenceStore
from ayeon.memory.retrieval_decoding_coordinator import (
    MemoryRetrievalDecodingCoordinator,
)
from ayeon.memory.retrieval_verifier import MemoryRetrievalVerifier
from ayeon.memory.sqlite_evidence_reader import SQLiteDurableMemoryEvidenceReader
from ayeon.memory.sqlite_repository import SQLiteMemoryRepository
from ayeon.memory.sqlite_retriever import SQLiteMemoryRetriever


def _search_words(text: str) -> set[str]:
    import re
    import unicodedata

    normalized = "".join(
        character
        for character in unicodedata.normalize("NFKD", text.casefold())
        if not unicodedata.combining(character)
    )
    ignored = {"que", "me", "el", "la", "los", "las", "un", "una", "de"}
    return set(re.findall(r"\w+", normalized)) - ignored


class KeywordEvaluator:
    """Conservative word matching for this console demo."""

    def evaluate(self, user_input, decoded):
        fact = decoded.content.get("fact")
        if not isinstance(fact, str):
            return MemoryContextRelevanceOutcome.UNKNOWN

        query_words = _search_words(user_input)
        fact_words = _search_words(fact)
        same_negation = ("no" in query_words) == ("no" in fact_words)

        if query_words and query_words <= fact_words and same_negation:
            return MemoryContextRelevanceOutcome.RELEVANT
        return MemoryContextRelevanceOutcome.UNKNOWN


def _verified_memory(record, persistence, database_path, reader):
    decoding = MemoryRetrievalDecodingCoordinator().retrieve_and_decode(
        record.memory_record_id,
        SQLiteMemoryRetriever(database_path),
    )
    retrieval_check = MemoryRetrievalVerifier(reader).verify(decoding)
    persistence_check = DeterministicMemoryPersistenceVerifier(reader).verify(
        record, persistence
    )
    eligibility = MemoryContextEligibilityPolicy().evaluate(
        record=record,
        retrieval_verification=retrieval_check,
        persistence_verification=persistence_check,
    )
    if eligibility.outcome is MemoryContextEligibilityOutcome.ELIGIBLE:
        return decoding.decoded
    return None



def main() -> None:
    with ExitStack() as stack:
        configured_path = os.getenv("AYEON_MEMORY_DB", "").strip()
        if configured_path:
            database_path = Path(configured_path).expanduser()
            database_path.parent.mkdir(parents=True, exist_ok=True)
            references = LocalMemoryReferenceStore(
                database_path.with_suffix(".references.jsonl")
            )
        else:
            directory = stack.enter_context(TemporaryDirectory())
            database_path = Path(directory) / "memory.db"
            references = None

        repository = SQLiteMemoryRepository(database_path)
        reader = SQLiteDurableMemoryEvidenceReader(database_path)
        saved = []
        if references is not None:
            for record in references.load():
                saved.append((
                    record,
                    MemoryPersistenceResult(
                        memory_record_id=record.memory_record_id,
                        repository_name=repository.name,
                        state=ResultState.UNKNOWN,
                        trace=record.trace,
                        summary="Reference restored; durable bytes require verification.",
                    ),
                ))
        use_gemini = os.getenv("AYEON_USE_GEMINI") == "1"
        engine = (
            TextCognitionEngine(GeminiGenerator())
            if use_gemini
            else DemoCognitionEngine()
        )
        coordinator = CognitionCoordinator(
            context_builder=ContextBuilder(),
            cognition_engine=engine,
        )
        sequence = 0

        if references is None:
            print("Ayeon · demo de memoria (solo durante esta sesión)")
        else:
            print("Ayeon · demo de memoria persistente")
        print("Comandos: guardar: <dato> | recordar: <palabra> | listar | olvidar: <id> | salir")

        while True:
            command = input("\nTú> ").strip()
            action, separator, value = command.partition(":")
            action = action.strip().casefold()
            value = value.strip()

            if action == "recuerda":
                action = "recordar"

            if not separator and command.casefold().startswith("recuerda "):
                action = "recordar"
                separator = ":"
                value = command[len("recuerda "):].strip()

            if not separator and command.casefold().startswith("recordar "):
                action = "recordar"
                separator = ":"
                value = command[len("recordar "):].strip()

            if command.casefold() == "salir":
                break

            if command.casefold() == "listar":
                listed = False
                for record, persistence in saved:
                    decoded = _verified_memory(
                        record, persistence, database_path, reader
                    )
                    if decoded is not None:
                        fact = decoded.content.get("fact")
                        if isinstance(fact, str):
                            print(f"Ayeon> {record.memory_record_id} | {fact}")
                            listed = True
                if not listed:
                    print("Ayeon> No hay recuerdos verificados.")
                continue

            if action == "olvidar":
                if not separator or not value:
                    print("Ayeon> Escribe olvidar: <id>")
                    continue

                selected = [
                    pair for pair in saved
                    if str(pair[0].memory_record_id) == value
                ]
                if len(selected) != 1:
                    print("Ayeon> No encontre ese recuerdo.")
                    continue

                record, persistence = selected[0]
                if _verified_memory(record, persistence, database_path, reader) is None:
                    print("Ayeon> No pude verificar ese recuerdo.")
                    continue
                if references is not None and not references.remove(record):
                    print("Ayeon> No pude retirar su referencia.")
                    continue
                if not repository.delete(record):
                    print("Ayeon> No pude retirar el registro.")
                    continue

                saved.remove(selected[0])
                print("Ayeon> Recuerdo eliminado.")
                continue

            if action == "guardar" and separator and value:
                normalized_value = " ".join(value.casefold().split())
                already_saved = False
                for saved_record, saved_persistence in saved:
                    decoded = _verified_memory(
                        saved_record, saved_persistence, database_path, reader
                    )
                    if decoded is None:
                        continue
                    existing_fact = decoded.content.get("fact")
                    if (
                        isinstance(existing_fact, str)
                        and " ".join(existing_fact.casefold().split())
                        == normalized_value
                    ):
                        already_saved = True
                        break

                if already_saved:
                    print("Ayeon> Ya existe ese dato guardado.")
                    continue

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
                    if references is not None:
                        try:
                            references.append(record)
                        except OSError:
                            print("Ayeon> No pude conservar la referencia del dato.")
                            continue
                    saved.append((record, persistence))
                    print("Ayeon> Guardé ese dato para esta sesión.")
                else:
                    print("Ayeon> No pude guardar ese dato.")
                continue

            if action == "recordar" and separator and not value:
                print("Ayeon> Escribe una palabra después de recordar:")
                continue
            if action == "recordar" and not separator:
                print("Ayeon> Escribe recordar: <palabra>")
                continue

            is_recall = action == "recordar" and separator and bool(value)
            is_memory_question = command.casefold().removeprefix("\u00bf").startswith(
                ("que me gusta", "qué me gusta")
            )
            if is_recall or is_memory_question:
                search_query = value if is_recall else command
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
                        user_input=search_query,
                        eligibility=eligibility,
                        decoded=decoding.decoded,
                        evaluator=LexicalMemoryRelevanceEvaluator(),
                    )
                    if relevance.outcome is MemoryContextRelevanceOutcome.RELEVANT:
                        fact = (
                            decoding.decoded.content.get("fact")
                            if decoding.decoded is not None
                            else None
                        )
                        if isinstance(fact, str):
                            matches.append(fact)

                if matches:
                    if use_gemini:
                        prompt = (
                            f"Pregunta del usuario: {search_query}\n"
                            "Recuerdos verificados relevantes:\n"
                            + "\n".join(f"- {fact}" for fact in matches)
                            + "\nResponde usando solo esos recuerdos. "
                            "Si no contienen la respuesta, dilo."
                        )
                        sequence += 1
                        output = coordinator.process(
                            trace=TraceContext.root(),
                            user_input=prompt,
                            state_snapshot=AyeonStateSnapshot(
                                sequence=sequence,
                                runtime_health=HealthState.HEALTHY,
                            ),
                        )
                        print(f"Ayeon> {output.spoken_response}")
                    else:
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
