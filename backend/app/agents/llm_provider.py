"""
LLM Provider V2 – Groq Pool + Gemini Fallback
===============================================

Model routing:
  GROQ_MODEL_ANALYZER = llama-3.3-70b   (100K TPD) – analyzer only
  GROQ_MODEL          = llama-4-scout    (500K TPD) – career, project, interview
  GROQ_MODEL_FAST     = llama-3.1-8b    (500K TPD) – improvement loop

Fallback chain on TPD / quota error:
  Groq → Gemini Flash (1M tokens/day free)

Gemini is ONLY activated when Groq returns a daily-limit error.
Normal 429 per-minute errors still rotate Groq keys as before.
"""
from __future__ import annotations
import os

GROQ_MODEL          = os.getenv("GROQ_MODEL",          "meta-llama/llama-4-scout-17b-16e-instruct")
GROQ_MODEL_ANALYZER = os.getenv("GROQ_MODEL_ANALYZER", "llama-3.3-70b-versatile")
GROQ_MODEL_FAST     = os.getenv("GROQ_MODEL_FAST",     "llama-3.1-8b-instant")
GEMINI_API_KEY      = os.getenv("GEMINI_API_KEY",      "")
GEMINI_MODEL        = os.getenv("GEMINI_MODEL",        "gemini-2.0-flash")


# ── Gemini builder ────────────────────────────────────────────────────────────

GEMINI_FALLBACK_MODELS = [
    os.getenv("GEMINI_MODEL", "gemini-2.0-flash-lite"),
    "gemini-1.5-flash",
    "gemini-1.5-flash-8b",
]

def _build_gemini(temperature: float, max_tokens: int):
    """Try Gemini models in order, with retry on 429."""
    import time
    if not GEMINI_API_KEY or GEMINI_API_KEY == "your_gemini_api_key_here":
        raise RuntimeError(
            "[LLMProvider] Both Groq and Gemini quotas exhausted. "
            "Add GEMINI_API_KEY to backend/.env"
        )
    from langchain_google_genai import ChatGoogleGenerativeAI

    last_exc = None
    for model in GEMINI_FALLBACK_MODELS:
        for attempt in range(3):
            try:
                llm = ChatGoogleGenerativeAI(
                    model=model,
                    google_api_key=GEMINI_API_KEY,
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                )
                print(f"[LLMProvider] Using Gemini model: {model}")
                return llm
            except Exception as exc:
                s = str(exc).lower()
                if "429" in s or "quota" in s or "resource_exhausted" in s:
                    wait = (attempt + 1) * 8
                    print(f"[LLMProvider] Gemini {model} quota hit, waiting {wait}s...")
                    time.sleep(wait)
                    last_exc = exc
                    continue
                raise
    raise RuntimeError(f"[LLMProvider] All Gemini models exhausted. Last: {last_exc}")


# ── Groq builder with Gemini fallback ─────────────────────────────────────────

def _build(model: str, temperature: float, max_tokens: int):
    """
    Try Groq first. On TPD (daily limit) → fall back to Gemini.
    On per-minute 429 → key rotation is handled inside _RotatingChatGroq.
    """
    from app.core.key_manager import key_manager

    class _GeminiFallbackProxy:
        """
        Wraps a _RotatingChatGroq and catches TPD errors at invoke-time,
        transparently switching to Gemini for the rest of that call.
        """
        def __init__(self, groq_llm):
            self._groq = groq_llm
            self._temp = temperature
            self._max  = max_tokens

        def _is_tpd(self, exc: Exception) -> bool:
            s = str(exc).lower()
            return (
                "tokens per day" in s or
                "per day" in s or
                "daily token limit" in s or
                "tpd" in s or
                "quota" in s
            )

        def invoke(self, messages, **kwargs):
            try:
                return self._groq.invoke(messages, **kwargs)
            except Exception as exc:
                if self._is_tpd(exc):
                    print(f"[LLMProvider] Groq TPD hit → switching to Gemini fallback.")
                    gemini = _build_gemini(self._temp, self._max)
                    return gemini.invoke(messages, **kwargs)
                raise

        def stream(self, messages, **kwargs):
            try:
                yield from self._groq.stream(messages, **kwargs)
            except Exception as exc:
                if self._is_tpd(exc):
                    print(f"[LLMProvider] Groq TPD hit → switching to Gemini fallback.")
                    gemini = _build_gemini(self._temp, self._max)
                    yield from gemini.stream(messages, **kwargs)
                else:
                    raise

        def with_structured_output(self, schema, **kwargs):
            # Structured output stays on Groq (Gemini path not needed for supervisor)
            return self._groq.with_structured_output(schema, **kwargs)

    groq_llm = key_manager.build_groq_llm(
        temperature=temperature, max_tokens=max_tokens, model=model
    )
    return _GeminiFallbackProxy(groq_llm)


# ── Public API ────────────────────────────────────────────────────────────────

def get_llm(temperature: float = 0.4, max_tokens: int = 2000):
    """llama-4-scout (500K TPD) → Gemini fallback. For career, project, interview."""
    return _build(GROQ_MODEL, temperature, max_tokens)


def get_llm_analyzer(temperature: float = 0.2, max_tokens: int = 1200):
    """llama-3.3-70b (100K TPD) → Gemini fallback. For analyzer only."""
    return _build(GROQ_MODEL_ANALYZER, temperature, max_tokens)


def get_llm_fast(temperature: float = 0.4, max_tokens: int = 1500):
    """llama-3.1-8b (500K TPD) → Gemini fallback. For improvement loop."""
    return _build(GROQ_MODEL_FAST, temperature, max_tokens)
