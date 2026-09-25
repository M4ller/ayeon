"""Deterministic lexical relevance evaluation for decoded memories."""

from __future__ import annotations

import re
import unicodedata

from ayeon.contracts.memory_context_relevance import (
    MemoryContextRelevanceOutcome,
)
from ayeon.contracts.memory_decoding import DecodedMemoryRecord

_CONCEPT_GROUPS = (
    {"salir", "irme", "irse", "ir", "voy"},
    {"cafe", "cafeteria"},
    {"comer", "comida"},
    {"gustar", "gusta", "favorito", "favorita"},
)


def _normalize_word(word: str) -> str:
    normalized = unicodedata.normalize("NFKD", word.casefold())
    return "".join(
        char
        for char in normalized
        if not unicodedata.combining(char)
    )


def _words(text: str) -> set[str]:
    return {
        _normalize_word(word)
        for word in re.findall(r"\w+", text, flags=re.UNICODE)
    }


def _expand_concepts(words: set[str]) -> set[str]:
    expanded = set(words)

    for group in _CONCEPT_GROUPS:
        if words & group:
            expanded.update(group)

    return expanded


class LexicalMemoryRelevanceEvaluator:
    """Evaluate memory relevance using normalized lexical concepts."""

    def evaluate(
        self,
        user_input: str,
        decoded: DecodedMemoryRecord,
    ) -> MemoryContextRelevanceOutcome:
        fact = decoded.content.get("fact")

        if not isinstance(fact, str):
            return MemoryContextRelevanceOutcome.UNKNOWN

        query_words = _expand_concepts(_words(user_input))
        fact_words = _expand_concepts(_words(fact))

        if not query_words:
            return MemoryContextRelevanceOutcome.UNKNOWN

        same_negation = ("no" in query_words) == ("no" in fact_words)

        if query_words & fact_words and same_negation:
            return MemoryContextRelevanceOutcome.RELEVANT

        return MemoryContextRelevanceOutcome.UNKNOWN
