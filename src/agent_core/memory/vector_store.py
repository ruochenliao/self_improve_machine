"""ChromaDB vector store for persistent memory."""

from __future__ import annotations

from typing import Any

import structlog

logger = structlog.get_logger()


class VectorStore:
    """Manages three ChromaDB collections: experiences, strategies, knowledge."""

    COLLECTIONS = ("experiences", "strategies", "knowledge")

    def __init__(self, persist_directory: str = "data/chromadb") -> None:
        self._persist_dir = persist_directory
        self._client = None
        self._collections: dict = {}

    def initialize(self) -> None:
        """Initialize ChromaDB client and collections."""
        try:
            import chromadb
            self._client = chromadb.PersistentClient(path=self._persist_dir)

            for name in self.COLLECTIONS:
                self._collections[name] = self._client.get_or_create_collection(
                    name=name,
                    metadata={"hnsw:space": "cosine"},
                )
            logger.info("vector_store.initialized", path=self._persist_dir)
        except ImportError:
            logger.warning("vector_store.chromadb_not_installed")
        except Exception as e:
            logger.error("vector_store.init_failed", error=str(e))

    def add(
        self,
        collection_name: str,
        text: str,
        metadata: dict | None = None,
        doc_id: str | None = None,
    ) -> str:
        """Add a document to a collection. Returns the document ID."""
        collection = self._collections.get(collection_name)
        if collection is None:
            raise ValueError(f"Collection '{collection_name}' not initialized")

        import uuid
        doc_id = doc_id or str(uuid.uuid4())
        meta = metadata or {"_source": "agent"}

        collection.add(
            documents=[text],
            metadatas=[meta],
            ids=[doc_id],
        )
        logger.debug("vector_store.added", collection=collection_name, id=doc_id)
        return doc_id

    def query(
        self,
        collection_name: str,
        query_text: str,
        n_results: int = 5,
        where_filter: dict | None = None,
    ) -> list[dict]:
        """Query a collection for similar documents."""
        collection = self._collections.get(collection_name)
        if collection is None:
            return []

        kwargs: dict = {
            "query_texts": [query_text],
            "n_results": min(n_results, collection.count() or n_results),
        }
        if where_filter:
            kwargs["where"] = where_filter

        if collection.count() == 0:
            return []

        results = collection.query(**kwargs)

        docs = []
        if results and results["documents"]:
            for i, doc in enumerate(results["documents"][0]):
                entry = {
                    "text": doc,
                    "id": results["ids"][0][i] if results["ids"] else "",
                    "distance": results["distances"][0][i] if results["distances"] else 0,
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                }
                docs.append(entry)

        return docs

    def update(self, collection_name: str, doc_id: str, text: str, metadata: dict | None = None) -> None:
        """Update an existing document."""
        collection = self._collections.get(collection_name)
        if collection is None:
            return

        update_kwargs: dict = {"ids": [doc_id], "documents": [text]}
        if metadata:
            update_kwargs["metadatas"] = [metadata]
        collection.update(**update_kwargs)

    def delete(self, collection_name: str, doc_id: str) -> None:
        """Delete a document by ID."""
        collection = self._collections.get(collection_name)
        if collection is None:
            return
        collection.delete(ids=[doc_id])

    def count(self, collection_name: str) -> int:
        """Get document count in a collection."""
        collection = self._collections.get(collection_name)
        if collection is None:
            return 0
        return collection.count()
