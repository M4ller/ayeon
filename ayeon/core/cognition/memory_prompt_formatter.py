"""Safe formatting of verified memory for cognition prompts."""

from __future__ import annotations

import json

from ayeon.contracts.memory_context_entry import MemoryContextEntry


class MemoryPromptFormatter:
    """Format verified memory as deterministic prompt data."""

    def format(
        self,
        memories: tuple[MemoryContextEntry, ...],
    ) -> str:
        if not memories:
            return ""

        blocks = []

        for entry in memories:
            content = json.dumps(
                dict(entry.decoded.content),
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            )

            blocks.append(
                "<memory>\n"
                f"{content}\n"
                "</memory>"
            )

        return "\n".join(blocks)