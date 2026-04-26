"""
ResumX V2 – ResumeCreator Agent (Onboarding Node)
==================================================

Triggered when: resume_raw is empty / onboarding_complete is False.

Behaviour:
  - Conversational agent that interviews the student across multiple turns
    to collect: personal info, education, skills, experience, projects, goals.
  - On each turn it appends to creator_conversation and returns the next
    question as an AIMessage.
  - When enough information is collected (≥ MIN_TURNS) it:
      1. Synthesises a professional resume string → resume_raw
      2. Dynamically creates RAG chunks for the new resume
      3. Sets onboarding_complete = True so the graph moves to the supervisor

The node is designed to be called repeatedly (one HTTP round-trip per turn)
until onboarding_complete flips to True.
"""
from __future__ import annotations

from typing import Dict, List

from langchain_core.messages import AIMessage

from app.agents.base_agent import BaseAgent
from app.agents.rag_store import RAGStore
from app.agents.state import AgentState

# Minimum conversation turns before attempting resume synthesis
MIN_TURNS = 6

_SYSTEM = """You are ResumX Onboarding Assistant – a warm, professional career coach.
Your job is to interview a student and collect everything needed to build their
first professional resume.

Collect (in order, one topic per turn):
  1. Full name, email, phone, LinkedIn/GitHub (optional)
  2. Education: degree, institution, graduation year, CGPA
  3. Technical skills (languages, frameworks, tools)
  4. Work experience or internships (if any)
  5. Projects: title, tech stack, brief description
  6. Career goal / target role

Rules:
  - Ask ONE focused question per turn. Be encouraging.
  - After collecting all 6 topics, output ONLY the JSON synthesis block.
  - Never fabricate information the student hasn't provided.
  - JSON synthesis format (wrap in ```json ... ```):
    {
      "resume_text": "<full professional resume as plain text>",
      "summary": "one-line profile summary"
    }
"""

_QUESTIONS = [
    "Hi! I'm your ResumX onboarding assistant. Let's build your resume together. "
    "What's your full name, email address, and phone number? "
    "(You can also share your LinkedIn or GitHub if you have one.)",

    "Great! Tell me about your education — your degree, institution, "
    "graduation year, and CGPA or percentage.",

    "What are your technical skills? List programming languages, frameworks, "
    "databases, tools, or any certifications you have.",

    "Have you done any internships or work experience? "
    "If yes, share the company name, role, duration, and key responsibilities. "
    "If not, just say 'No experience yet' and we'll focus on projects.",

    "Tell me about your best project(s). For each one: title, tech stack used, "
    "and a brief description of what it does.",

    "Finally, what's your target role or career goal? "
    "(e.g. 'Backend Developer at a product startup', 'Data Analyst at a bank')",
]


class ResumeCreatorAgent(BaseAgent):

    def __init__(self) -> None:
        super().__init__("resume_creator", _SYSTEM, temperature=0.5, max_tokens=3000)

    def run(self, state: AgentState) -> dict:
        conversation: List[Dict[str, str]] = list(
            state.get("creator_conversation") or []
        )
        turn = len([m for m in conversation if m.get("role") == "assistant"])

        # ── Still collecting information ──────────────────────────────────────
        if turn < len(_QUESTIONS):
            question = _QUESTIONS[turn]
            conversation.append({"role": "assistant", "content": question})
            return {
                "creator_conversation": conversation,
                "onboarding_complete":  False,
                "messages": [AIMessage(content=question, name="resume_creator")],
                "agent_history": [{"agent": "resume_creator",
                                   "action": "ask",
                                   "result": f"turn {turn + 1}/{len(_QUESTIONS)}"}],
            }

        # ── Enough turns – synthesise the resume ─────────────────────────────
        if turn >= MIN_TURNS:
            return self._synthesise(state, conversation)

        # Edge case: more turns needed but questions exhausted
        followup = ("Thanks for sharing all that! Just to confirm — "
                    "is there anything else you'd like to add to your resume "
                    "before I generate it?")
        conversation.append({"role": "assistant", "content": followup})
        return {
            "creator_conversation": conversation,
            "onboarding_complete":  False,
            "messages": [AIMessage(content=followup, name="resume_creator")],
            "agent_history": [{"agent": "resume_creator",
                                "action": "followup",
                                "result": "awaiting final confirmation"}],
        }

    def _synthesise(self, state: AgentState,
                    conversation: List[Dict[str, str]]) -> dict:
        """Build the resume from the collected conversation."""
        history_text = "\n".join(
            f"{m['role'].upper()}: {m['content']}"
            for m in conversation
        )
        prompt = (
            f"Based on the following interview conversation, "
            f"generate a complete professional resume.\n\n"
            f"CONVERSATION:\n{history_text}\n\n"
            f"Return ONLY the JSON synthesis block as described in your instructions."
        )

        try:
            raw  = self._call_llm(prompt, max_tokens=3000)
            data = self._parse_json(raw)
            resume_text = data.get("resume_text", "")
        except Exception as exc:
            resume_text = f"[Resume generation failed: {exc}]"

        # Dynamically index the new resume into RAG
        store = RAGStore.reset()
        store.index_documents(resume_text, state.get("job_description", ""))
        rag_chunks = store.chunks

        conversation.append({
            "role": "assistant",
            "content": "Your resume has been created! Let's now analyse it against your target role.",
        })

        return {
            "resume_raw":           resume_text,
            "rag_chunks":           rag_chunks,
            "creator_conversation": conversation,
            "onboarding_complete":  True,
            "messages": [AIMessage(
                content="Resume created and indexed. Proceeding to analysis.",
                name="resume_creator",
            )],
            "agent_history": [{"agent": "resume_creator",
                                "action": "synthesise",
                                "result": f"resume built ({len(resume_text)} chars)"}],
            "completed_agents": self._mark_done(state, "resume_creator"),
        }


def creator_node(state: AgentState) -> dict:
    return ResumeCreatorAgent().run(state)
