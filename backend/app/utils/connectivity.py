"""
Connectivity checker – detects internet availability at runtime.

Used by both the direct API services and the multi-agent LLM provider
to automatically switch between Groq (online) and Ollama (offline).
"""
from __future__ import annotations

import socket
import threading
import time
from typing import Optional

# ── Config ────────────────────────────────────────────────────────────────────

_CHECK_HOST = "api.groq.com"
_CHECK_PORT = 443
_TIMEOUT    = 3       # seconds per check
_CACHE_TTL  = 30      # re-check every 30 seconds

# ── Internal state ────────────────────────────────────────────────────────────

_cache_lock   = threading.Lock()
_last_checked: float = 0.0
_last_result:  bool  = False


def is_online() -> bool:
    """
    Return True if the Groq API endpoint is reachable.
    Result is cached for 30 seconds to avoid hammering the network check.
    """
    global _last_checked, _last_result

    now = time.monotonic()
    with _cache_lock:
        if now - _last_checked < _CACHE_TTL:
            return _last_result

        result = _check_connection()
        _last_checked = now
        _last_result  = result
        return result


def _check_connection() -> bool:
    """Low-level TCP probe to api.groq.com:443."""
    try:
        socket.setdefaulttimeout(_TIMEOUT)
        with socket.create_connection((_CHECK_HOST, _CHECK_PORT), timeout=_TIMEOUT):
            return True
    except (socket.timeout, socket.error, OSError):
        return False


def backend_label() -> str:
    """Human-readable label for logging."""
    return "groq (online)" if is_online() else "ollama (offline)"
