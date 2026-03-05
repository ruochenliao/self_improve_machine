"""Tests for the memory system: vector store, RAG, experience manager."""

from __future__ import annotations

import pytest
from pathlib import Path


@pytest.fixture
def vector_store(tmp_data_dir: Path):
    """Provide a fresh VectorStore backed by temp directory."""
    from agent_core.memory.vector_store import VectorStore
    store = VectorStore(str(tmp_data_dir / "chromadb_test"))
    store.initialize()
    return store


@pytest.fixture
def rag_engine(vector_store):
    """Provide a RAGEngine backed by the test vector store."""
    from agent_core.memory.rag import RAGEngine
    return RAGEngine(vector_store, top_k=3)


@pytest.fixture
def experience_mgr(vector_store):
    """Provide an ExperienceManager backed by the test vector store."""
    from agent_core.memory.experience import ExperienceManager
    return ExperienceManager(vector_store)


class TestVectorStore:
    """Test ChromaDB vector store operations."""

    def test_initialize_creates_collections(self, vector_store):
        for name in ("experiences", "strategies", "knowledge"):
            assert vector_store.count(name) == 0

    def test_add_and_count(self, vector_store):
        doc_id = vector_store.add("experiences", "test experience", {"success": True})
        assert doc_id
        assert vector_store.count("experiences") == 1

    def test_add_multiple(self, vector_store):
        vector_store.add("knowledge", "Python is a programming language")
        vector_store.add("knowledge", "asyncio provides async capabilities")
        vector_store.add("knowledge", "SQLite is a lightweight database")
        assert vector_store.count("knowledge") == 3

    def test_query_returns_results(self, vector_store):
        vector_store.add("knowledge", "Python is great for AI development")
        vector_store.add("knowledge", "JavaScript is used for web development")

        results = vector_store.query("knowledge", "AI programming", n_results=2)
        assert len(results) > 0
        assert "text" in results[0]
        assert "distance" in results[0]

    def test_query_empty_collection(self, vector_store):
        results = vector_store.query("experiences", "anything")
        assert results == []

    def test_update_document(self, vector_store):
        doc_id = vector_store.add("experiences", "original text")
        vector_store.update("experiences", doc_id, "updated text")
        results = vector_store.query("experiences", "updated", n_results=1)
        assert len(results) == 1
        assert "updated" in results[0]["text"]

    def test_delete_document(self, vector_store):
        doc_id = vector_store.add("experiences", "to be deleted")
        assert vector_store.count("experiences") == 1
        vector_store.delete("experiences", doc_id)
        assert vector_store.count("experiences") == 0

    def test_invalid_collection_raises(self, vector_store):
        with pytest.raises(ValueError):
            vector_store.add("nonexistent", "text")

    def test_query_nonexistent_collection(self, vector_store):
        results = vector_store.query("nonexistent", "test")
        assert results == []


class TestRAGEngine:
    """Test RAG retrieval engine."""

    def test_retrieve_with_empty_store(self, rag_engine):
        results = rag_engine.retrieve("test query")
        assert results == []

    def test_retrieve_returns_relevant(self, vector_store, rag_engine):
        vector_store.add("experiences", "Successfully deployed to AWS EC2")
        vector_store.add("experiences", "Fixed a Python syntax error in config.py")
        vector_store.add("knowledge", "AWS requires IAM credentials for API access")

        results = rag_engine.retrieve("AWS deployment")
        assert len(results) > 0

    def test_retrieve_respects_top_k(self, vector_store, rag_engine):
        for i in range(10):
            vector_store.add("knowledge", f"Knowledge item number {i}")

        results = rag_engine.retrieve("knowledge item")
        assert len(results) <= 3  # top_k=3 in fixture


class TestExperienceManager:
    """Test experience recording and strategy promotion."""

    def test_record_experience(self, experience_mgr):
        doc_id = experience_mgr.record(
            action="shell(ls -la)",
            result="file listing output",
            success=True,
            reflection="Successfully listed files",
        )
        assert doc_id

    def test_record_failed_experience(self, experience_mgr):
        doc_id = experience_mgr.record(
            action="http_request(invalid_url)",
            result="Connection error",
            success=False,
        )
        assert doc_id

    def test_strategy_promotion(self, experience_mgr):
        # Record enough successes to trigger promotion
        for i in range(4):
            experience_mgr.record(
                action="code_review(python)",
                result=f"Review completed {i}",
                success=True,
            )

        from agent_core.memory.vector_store import VectorStore
        stats = experience_mgr.get_stats()
        assert stats["experiences"] == 4
        # After 3+ successes, should be promoted to strategy
        assert stats["strategies"] >= 1

    def test_add_knowledge(self, experience_mgr):
        doc_id = experience_mgr.add_knowledge(
            "Stripe API requires webhook signature verification",
            category="payment",
        )
        assert doc_id

    def test_get_stats(self, experience_mgr):
        experience_mgr.record("test", "ok", True)
        stats = experience_mgr.get_stats()
        assert "experiences" in stats
        assert "strategies" in stats
        assert "knowledge" in stats
