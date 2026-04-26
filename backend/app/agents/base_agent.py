"""
BaseAgent – shared foundation for all five specialist nodes.

Uses ChatOllama (local) or ChatGroq (cloud) via LLMProvider.
All agents are backend-agnostic – swap LLM_BACKEND in .env, nothing else changes.
"""
from __future__ import annotations

import json
import re
from typing import Any, Dict, List

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from app.agents.llm_provider import get_llm
from app.agents.rag_store import RAGStore
from app.agents.state import AgentState


class BaseAgent:

    def __init__(self, name: str, system_prompt: str,
                 temperature: float = 0.4, max_tokens: int = 2000):
        self.name = name
        self.system_prompt = system_prompt
        self._temperature = temperature
        self._max_tokens = max_tokens

    # ── LLM call (backend-agnostic) ───────────────────────────────────────────

    def _call_llm(self, user_prompt: str, max_tokens: int | None = None) -> str:
        """
        Invoke the configured LLM (Ollama or Groq) and return the raw string.
        Uses LangChain's unified .invoke() interface.
        """
        llm = get_llm(
            temperature=self._temperature,
            max_tokens=max_tokens or self._max_tokens,
        )
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=user_prompt),
        ]
        response = llm.invoke(messages)
        return response.content.strip()

    # ── RAG (shared singleton – no redundant indexing) ────────────────────────

    def _get_rag_context(self, state: AgentState, query: str, top_k: int = 5) -> str:
        """
        Returns the pre-fetched rag_context from state if present,
        otherwise queries the singleton FAISS store directly.
        """
        cached = state.get("rag_context", "")
        if cached:
            return cached
        return RAGStore.instance().retrieve_as_context(query, top_k)

    # ── Deterministic JSON parser ─────────────────────────────────────────────

    def _parse_json(self, raw: str) -> Dict[str, Any]:
        """
        Robust JSON parser that handles:
          - Markdown fences (```json ... ```)
          - Control characters / emoji inside string values
          - Partial JSON (extracts outermost { … })
          - Truncated JSON (resume text too long for token budget)
        """
        cleaned = raw.strip()

        # 1. Strip ALL markdown fences (handles nested fences inside resume text)
        fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", cleaned)
        if fence_match:
            cleaned = fence_match.group(1).strip()

        # 2. Remove ASCII control characters that break json.loads
        #    but KEEP \n \r \t which are valid inside JSON strings
        cleaned = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", cleaned)

        # 3. Direct parse
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass

        # 4. Extract outermost { … } (handles leading/trailing prose)
        s = cleaned.find("{")
        e = cleaned.rfind("}") + 1
        if s >= 0 and e > s:
            candidate = cleaned[s:e]
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                pass

            # 5. Truncated JSON recovery – find last complete key-value pair
            #    and close the object.  Useful when resume text hits token limit.
            try:
                # Walk backwards to find last complete "key": "value" or "key": [...]
                last_comma = max(candidate.rfind(","), candidate.rfind('"'))
                if last_comma > s:
                    truncated = candidate[:last_comma].rstrip(", \n\r\t") + "\n}"
                    return json.loads(truncated)
            except (json.JSONDecodeError, ValueError):
                pass

        raise ValueError(
            f"[{self.name}] Cannot parse JSON from LLM output: {raw[:300]}"
        )

    # ── Hallucination guardrail ───────────────────────────────────────────────

    @staticmethod
    def _facts_block(state: AgentState) -> str:
        """
        Injects verified_facts into every prompt.
        Agents are instructed to only reference information from this list.
        """
        facts = state.get("verified_facts", [])
        if not facts:
            return ""
        lines = "\n".join(f"  • {f}" for f in facts[:20])
        return (
            "\n\nVERIFIED RESUME FACTS – only reference information from this list:\n"
            + lines
        )

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _make_result_message(self, summary: str) -> AIMessage:
        return AIMessage(content=summary, name=self.name)

    @staticmethod
    def _mark_done(state: AgentState, agent_name: str) -> List[str]:
        return state.get("completed_agents", []) + [agent_name]
