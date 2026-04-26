"""
ResumX V2 – ResumxKeyManager (Groq Pool)
=========================================

Loads a pool of up to 25 Groq API keys from .env.
Every LLM call pulls a random key from the ACTIVE pool.
On a 429 Rate-Limit response the offending key is blacklisted for
BLACKLIST_TTL seconds and the call is immediately retried with a
fresh key – guaranteeing 100% uptime during high-traffic hackathons.

.env format:
  GROQ_API_KEY_1=gsk_...
  GROQ_API_KEY_2=gsk_...
  ...
  GROQ_API_KEY_25=gsk_...
  (legacy single key also supported: GROQ_API_KEY=gsk_...)

Usage:
  from app.core.key_manager import key_manager
  key = key_manager.get_key()          # random active key
  key_manager.blacklist(key)           # call on 429
"""
from __future__ import annotations

import os
import random
import threading
import time
from typing import Dict, List, Optional

# How long (seconds) a rate-limited key stays blacklisted before re-admission
BLACKLIST_TTL: int = int(os.getenv("GROQ_BLACKLIST_TTL", "60"))
MAX_RETRIES:   int = int(os.getenv("GROQ_MAX_RETRIES",   "5"))


class ResumxKeyManager:
    """
    Thread-safe Groq API key pool with automatic rotation and blacklisting.
    """

    def __init__(self) -> None:
        self._lock: threading.Lock = threading.Lock()
        self._pool: List[str]      = []
        # key → unix timestamp when it was blacklisted
        self._blacklist: Dict[str, float] = {}
        self._load_keys()

    # ── Key loading ───────────────────────────────────────────────────────────

    def _load_keys(self) -> None:
        """
        Collect all GROQ_API_KEY_N keys from environment.
        Falls back to the legacy GROQ_API_KEY if no numbered keys found.
        """
        keys: List[str] = []

        # Numbered pool: GROQ_API_KEY_1 … GROQ_API_KEY_25
        for i in range(1, 26):
            val = os.getenv(f"GROQ_API_KEY_{i}", "").strip()
            if val:
                keys.append(val)

        # Legacy single key
        legacy = os.getenv("GROQ_API_KEY", "").strip()
        if legacy and legacy not in keys:
            keys.append(legacy)

        if not keys:
            raise EnvironmentError(
                "[KeyManager] No Groq API keys found. "
                "Set GROQ_API_KEY or GROQ_API_KEY_1 … GROQ_API_KEY_25 in .env"
            )

        self._pool = keys
        print(f"[KeyManager] Loaded {len(self._pool)} Groq API key(s).")

    # ── Blacklist helpers ─────────────────────────────────────────────────────

    def _is_blacklisted(self, key: str) -> bool:
        """Return True if key is still within its blacklist TTL."""
        ts = self._blacklist.get(key)
        if ts is None:
            return False
        if time.time() - ts < BLACKLIST_TTL:
            return True
        # TTL expired – re-admit the key
        del self._blacklist[key]
        return False

    def blacklist(self, key: str) -> None:
        """Temporarily blacklist a key after a 429 response."""
        with self._lock:
            self._blacklist[key] = time.time()
            print(f"[KeyManager] Key ...{key[-6:]} blacklisted for {BLACKLIST_TTL}s")

    # ── Key retrieval ─────────────────────────────────────────────────────────

    def get_key(self) -> str:
        """
        Return a random active (non-blacklisted) key.
        Raises RuntimeError if ALL keys are currently blacklisted.
        """
        with self._lock:
            active = [k for k in self._pool if not self._is_blacklisted(k)]
            if not active:
                # All keys exhausted – wait for the earliest TTL to expire
                earliest = min(self._blacklist.values())
                wait = max(0.0, BLACKLIST_TTL - (time.time() - earliest)) + 1
                print(f"[KeyManager] All keys blacklisted. Waiting {wait:.1f}s …")
                time.sleep(wait)
                # Re-evaluate after wait
                active = [k for k in self._pool if not self._is_blacklisted(k)]
                if not active:
                    raise RuntimeError("[KeyManager] All Groq keys are rate-limited.")
            return random.choice(active)

    # ── Retry-aware LLM builder ───────────────────────────────────────────────

    def build_groq_llm(self, temperature: float = 0.4, max_tokens: int = 2000,
                       model: str = None):
        """Return a _RotatingChatGroq proxy for the given model."""
        model = model or os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        return _RotatingChatGroq(
            manager=self,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    # ── Status report ─────────────────────────────────────────────────────────

    def status(self) -> dict:
        """Return pool health summary (useful for /api/health endpoint)."""
        with self._lock:
            active_count = sum(
                1 for k in self._pool if not self._is_blacklisted(k)
            )
            return {
                "total_keys":      len(self._pool),
                "active_keys":     active_count,
                "blacklisted_keys": len(self._pool) - active_count,
            }


# ── Rotating proxy ────────────────────────────────────────────────────────────

class _RotatingChatGroq:
    """
    Thin wrapper around ChatGroq that catches 429s at .invoke() / .stream() time,
    blacklists the offending key, and retries with a fresh one.
    Implements the same interface LangChain expects (invoke, stream, with_structured_output).
    """

    def __init__(self, manager: "ResumxKeyManager", model: str,
                 temperature: float, max_tokens: int) -> None:
        self._manager     = manager
        self._model       = model
        self._temperature = temperature
        self._max_tokens  = max_tokens

    def _build(self):
        from langchain_groq import ChatGroq
        return ChatGroq(
            api_key=self._manager.get_key(),
            model=self._model,
            temperature=self._temperature,
            max_tokens=self._max_tokens,
        )

    def _is_rate_limit(self, exc: Exception) -> bool:
        s = str(exc).lower()
        return "429" in s or "rate_limit" in s or "rate limit" in s or "quota" in s

    def _is_daily_limit(self, exc: Exception) -> bool:
        """TPD = tokens per day — org-wide, rotating keys won't help."""
        s = str(exc).lower()
        return "tokens per day" in s or "tpd" in s or "per day" in s

    def _key_from_llm(self, llm) -> str:
        """Extract plain string key from ChatGroq instance (handles SecretStr)."""
        raw = llm.groq_api_key
        # langchain-groq >= 0.1.x wraps the key in pydantic SecretStr
        if hasattr(raw, "get_secret_value"):
            return raw.get_secret_value()
        return str(raw)

    def invoke(self, messages, **kwargs):
        last_exc: Optional[Exception] = None
        for attempt in range(1, MAX_RETRIES + 1):
            llm = self._build()
            try:
                return llm.invoke(messages, **kwargs)
            except Exception as exc:
                if self._is_daily_limit(exc):
                    # TPD is org-wide — rotating keys won't help, raise immediately
                    raise RuntimeError(
                        f"[Groq] Daily token limit reached. "
                        f"Quota resets in ~1 hour. Error: {exc}"
                    ) from exc
                if self._is_rate_limit(exc):
                    print(f"[KeyManager] 429 on invoke attempt {attempt}/{MAX_RETRIES}. Rotating.")
                    self._manager.blacklist(self._key_from_llm(llm))
                    last_exc = exc
                    continue
                raise
        raise RuntimeError(f"[KeyManager] All retries exhausted. Last: {last_exc}")

    def stream(self, messages, **kwargs):
        last_exc: Optional[Exception] = None
        for attempt in range(1, MAX_RETRIES + 1):
            llm = self._build()
            try:
                yield from llm.stream(messages, **kwargs)
                return
            except Exception as exc:
                if self._is_daily_limit(exc):
                    raise RuntimeError(
                        f"[Groq] Daily token limit reached. "
                        f"Quota resets in ~1 hour. Error: {exc}"
                    ) from exc
                if self._is_rate_limit(exc):
                    print(f"[KeyManager] 429 on stream attempt {attempt}/{MAX_RETRIES}. Rotating.")
                    self._manager.blacklist(self._key_from_llm(llm))
                    last_exc = exc
                    continue
                raise
        raise RuntimeError(f"[KeyManager] All retries exhausted. Last: {last_exc}")

    def with_structured_output(self, schema, **kwargs):
        """
        Returns a proxy that applies structured output on each retry attempt.
        Used by the Supervisor for RouteDecision.
        """
        return _StructuredOutputProxy(self, schema, kwargs)


class _StructuredOutputProxy:
    """Proxy for .with_structured_output() that also rotates on 429."""

    def __init__(self, parent: _RotatingChatGroq, schema, kwargs: dict) -> None:
        self._parent = parent
        self._schema = schema
        self._kwargs = kwargs

    def invoke(self, messages, **kw):
        last_exc: Optional[Exception] = None
        used_keys: List[str] = []
        for attempt in range(1, MAX_RETRIES + 1):
            key = self._parent._manager.get_key()
            used_keys.append(key)
            from langchain_groq import ChatGroq
            raw_llm = ChatGroq(
                api_key=key,
                model=self._parent._model,
                temperature=self._parent._temperature,
                max_tokens=self._parent._max_tokens,
            )
            llm = raw_llm.with_structured_output(self._schema, **self._kwargs)
            try:
                return llm.invoke(messages, **kw)
            except Exception as exc:
                if self._parent._is_rate_limit(exc):
                    print(f"[KeyManager] 429 on structured attempt {attempt}/{MAX_RETRIES}. Rotating.")
                    self._parent._manager.blacklist(key)
                    last_exc = exc
                    continue
                raise
        raise RuntimeError(f"[KeyManager] All retries exhausted. Last: {last_exc}")


# ── Module-level singleton ────────────────────────────────────────────────────
# Import this everywhere: `from app.core.key_manager import key_manager`
key_manager = ResumxKeyManager()
