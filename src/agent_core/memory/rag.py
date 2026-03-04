"""RAG (Retrieval Augmented Generation) engine for memory retrieval."""

from __future__ import annotations

from typing import TYPE_CHECKING

import structlog

if TYPE_CHECKING:
    from agent_core.memory.vector_store import VectorStore

logger = structlog.get_logger()


class RAGEngine:
    """Retrieves relevant memories and formats them for context injection."""

    def __init__(self, vector_store: VectorStore, top_k: int = 5) -> None:
        self._store = vector_store
        self._top_k = top_k

    def retrieve(
        self,
        query_text: str,
        memory_types: list[str] | None = None,
        top_k: int | None = None,
    ) -> list[dict]:
        """Retrieve relevant memories from specified collections.

        Args:
            query_text: The query to search for
            memory_types: Which collections to search (default: all)
            top_k: Number of results per collection (default: self._top_k)
        """
        types = memory_types or ["experiences", "strategies", "knowledge"]
        k = top_k or self._top_k
        all_results: list[dict] = []

        for mem_type in types:
            results = self._store.query(mem_type, query_text, n_results=k)
            for r in results:
                r["memory_type"] = mem_type
            all_results.extend(results)

        # Sort by distance (lower = more relevant)
        all_results.sort(key=lambda x: x.get("distance", float("inf")))

        # Return top_k overall
        return all_results[:k]

    def format_memories(self, memories: list[dict]) -> str:
        """Format retrieved memories as markdown text for context injection."""
        if not memories:
            return ""

        sections: dict[str, list[str]] = {
            "experiences": [],
            "strategies": [],
            "knowledge": [],
        }

        for mem in memories:
            mem_type = mem.get("memory_type", "experiences")
            text = mem.get("text", "")
            if text and mem_type in sections:
                sections[mem_type].append(f"- {text}")

        parts: list[str] = []
        type_labels = {
            "experiences": "Past Experiences",
            "strategies": "Proven Strategies",
            "knowledge": "Acquired Knowledge",
        }

        for mem_type, items in sections.items():
            if items:
                label = type_labels.get(mem_type, mem_type)
                parts.append(f"### {label}")
                parts.extend(items)
                parts.append("")

        if parts:
            return "## Relevant Memories\n\n" + "\n".join(parts)
        return ""

    def retrieve_and_format(
        self,
        query_text: str,
        memory_types: list[str] | None = None,
    ) -> str:
        """Retrieve and format in one call."""
        memories = self.retrieve(query_text, memory_types)
        return self.format_memories(memories)
