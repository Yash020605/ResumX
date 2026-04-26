"""
RAGStore – true Singleton FAISS vector store shared by all agents.

All agents call RAGStore.instance() to get the same object.
The store is re-indexed once per analysis session via index_documents().
Agents retrieve context via retrieve(query) – no redundant indexing.

Falls back to keyword overlap when faiss / sentence-transformers are absent.
"""
from __future__ import annotations

import threading
from typing import Dict, List, Optional

import numpy as np

try:
    import faiss
    from sentence_transformers import SentenceTransformer
    _FAISS_OK = True
except ImportError:
    _FAISS_OK = False


class RAGStore:
    """
    Thread-safe Singleton FAISS store.

    Usage:
        store = RAGStore.instance()
        store.index_documents(resume, job_description)
        chunks = store.retrieve("Python skills", top_k=5)
        facts  = store.extract_verified_facts(resume)
    """

    _instance: Optional[RAGStore] = None
    _lock: threading.Lock = threading.Lock()

    # ── Singleton constructor ─────────────────────────────────────────────────

    def __new__(cls) -> RAGStore:
        raise RuntimeError("Use RAGStore.instance() – do not instantiate directly.")

    @classmethod
    def instance(cls) -> RAGStore:
        """Return the global singleton, creating it on first call."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    obj = object.__new__(cls)
                    obj._init_store()
                    cls._instance = obj
        return cls._instance

    @classmethod
    def reset(cls) -> RAGStore:
        """
        Destroy the current singleton and create a fresh one.
        Call this at the start of every new analysis session.
        """
        with cls._lock:
            obj = object.__new__(cls)
            obj._init_store()
            cls._instance = obj
        return cls._instance

    # ── Internal init ─────────────────────────────────────────────────────────

    def _init_store(self) -> None:
        self.chunks: List[str] = []
        self.metadata: List[Dict] = []
        self._index = None
        self._model = None
        self._dim: int = 0

        if _FAISS_OK:
            try:
                self._model = SentenceTransformer("all-MiniLM-L6-v2")
            except Exception as e:
                print(f"[RAGStore] SentenceTransformer failed ({e}). Using keyword fallback.")

    # ── Indexing ──────────────────────────────────────────────────────────────

    def index_documents(self, resume: str, job_description: str = "") -> List[str]:
        """
        Chunk and embed the resume + JD into FAISS.
        Returns the full list of stored chunks.
        """
        self.chunks = []
        self.metadata = []

        def _add(text: str, source: str) -> None:
            for i, para in enumerate(text.split("\n\n")):
                para = para.strip()
                if para:
                    self.chunks.append(para)
                    self.metadata.append({"source": source, "index": i})

        _add(resume, "resume")
        if job_description:
            _add(job_description, "job_description")

        if _FAISS_OK and self._model and self.chunks:
            embeddings = self._model.encode(self.chunks, convert_to_numpy=True).astype(np.float32)
            self._dim = embeddings.shape[1]
            self._index = faiss.IndexFlatL2(self._dim)
            self._index.add(embeddings)

        return self.chunks

    # ── Retrieval ─────────────────────────────────────────────────────────────

    def retrieve(self, query: str, top_k: int = 5) -> List[str]:
        """Return the top-k most relevant chunks for a query."""
        if not self.chunks:
            return []
        if _FAISS_OK and self._model and self._index is not None:
            return self._faiss_retrieve(query, top_k)
        return self._keyword_retrieve(query, top_k)

    def retrieve_as_context(self, query: str, top_k: int = 5) -> str:
        """Convenience wrapper – returns chunks joined as a single string."""
        return "\n---\n".join(self.retrieve(query, top_k))

    def _faiss_retrieve(self, query: str, top_k: int) -> List[str]:
        q_vec = self._model.encode([query], convert_to_numpy=True).astype(np.float32)
        k = min(top_k, len(self.chunks))
        _, idxs = self._index.search(q_vec, k)
        return [self.chunks[i] for i in idxs[0] if 0 <= i < len(self.chunks)]

    def _keyword_retrieve(self, query: str, top_k: int) -> List[str]:
        q_words = set(query.lower().split())
        scored = sorted(
            self.chunks,
            key=lambda c: len(q_words & set(c.lower().split())),
            reverse=True,
        )
        return scored[:top_k]

    # ── Fact extraction ───────────────────────────────────────────────────────

    def extract_verified_facts(self, resume: str) -> List[str]:
        """
        Extract concrete, verifiable statements from the resume.
        These are injected into every agent prompt as a hallucination guardrail.
        """
        facts = [
            line.strip()
            for line in resume.splitlines()
            if len(line.strip()) > 20 and not line.strip().startswith("#")
        ]
        return facts[:40]
