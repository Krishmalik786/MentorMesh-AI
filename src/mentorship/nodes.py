"""
Phase 3 mentorship graph nodes.

coordinator      — LLM decides which specialist(s) are relevant to the question
specialist       — one node, reused per specialist via LangGraph's Send fan-out;
                    each run only sees its own slice of the profile + evidence
synthesizer      — merges specialist response(s) into one coherent reply
grounding_check  — plain code, same instinct as Phase 2's validate_node:
                    checks the draft reply's claims against evidence_log
                    before it's allowed to reach the founder
"""

import re
from typing import Literal

from langgraph.types import Send
from pydantic import BaseModel, Field

from src.llm_client import get_llm
from src.mentorship.state import MentorshipState
from src.profile_schema import SourceType

MAX_RETRIES = 2

SPECIALIST_CONFIG = {
    "technical": {
        "source": SourceType.GITHUB,
        "profile_field": "technical",
        "persona": "a technical/engineering mentor, focused on code health, architecture, and dev practices",
    },
    "product": {
        "source": SourceType.WEBSITE,
        "profile_field": "product",
        "persona": "a product and market-fit mentor, focused on positioning, value proposition, and target market",
    },
    "pitch": {
        "source": SourceType.PITCH_DECK,
        "profile_field": "pitch",
        "persona": "a fundraising and pitch mentor, focused on narrative, traction evidence, and investor readiness",
    },
    "growth": {
        "source": SourceType.SOCIAL,
        "profile_field": "social",
        "persona": "a growth and audience mentor, focused on social presence and engagement",
    },
}


class RoutingDecision(BaseModel):
    specialists: list[Literal["technical", "product", "pitch", "growth"]] = Field(
        description="Which mentor specialists are actually relevant to answering this question. "
        "Usually 1-2 — only include a specialist if the question genuinely touches their area."
    )


def coordinator_node(state: MentorshipState) -> dict:
    llm = get_llm()
    structured_llm = llm.with_structured_output(RoutingDecision)

    profile = state["profile"]
    prompt = f"""A founder is chatting with a startup mentorship copilot.

Startup: {profile.company_name or "Unknown"} — {profile.one_line_summary or "no summary yet"}

Founder's question: "{state['question']}"

Decide which mentor specialist(s) should answer this — technical (code/engineering),
product (positioning/market fit), pitch (fundraising/narrative), growth (social/audience)."""

    decision = structured_llm.invoke(prompt)
    return {"specialists_to_run": decision.specialists}


def route_to_specialists(state: MentorshipState) -> list[Send]:
    specialists = state["specialists_to_run"] or ["product"]
    return [Send("specialist", {**state, "specialist_key": key}) for key in specialists]


def specialist_node(state: dict) -> dict:
    key = state["specialist_key"]
    config = SPECIALIST_CONFIG[key]
    profile = state["profile"]

    section = getattr(profile, config["profile_field"])
    relevant_evidence = [e.claim for e in profile.evidence_log if e.source == config["source"]]

    llm = get_llm()
    prompt = f"""You are {config['persona']} at a startup mentorship copilot.

Only use the data below — if it doesn't cover what's being asked, say so honestly
rather than giving generic advice. Cite specifics when you make a claim.

Relevant profile data:
{section.model_dump_json(indent=2)}

Supporting evidence:
{chr(10).join(f"- {e}" for e in relevant_evidence) or "(none available)"}

Founder's question: "{state['question']}"

Give a short (2-4 sentence), direct, evidence-cited response."""

    response = llm.invoke(prompt)
    return {"specialist_responses": {key: response.content}}


def synthesizer_node(state: MentorshipState) -> dict:
    responses = state["specialist_responses"]

    if len(responses) == 1:
        draft = next(iter(responses.values()))
    else:
        llm = get_llm()
        combined = "\n\n".join(f"[{key} mentor]: {text}" for key, text in responses.items())
        feedback = ""
        if state.get("grounding_issues"):
            feedback = "\n\nThe previous draft had these problems — fix them:\n" + "\n".join(
                f"- {e}" for e in state["grounding_issues"]
            )
        prompt = f"""Merge these specialist mentor responses into one coherent, conversational
reply to the founder. Don't just concatenate them — blend into a natural response,
keep it concise, keep every specific/evidence-cited claim.

{combined}

Founder's original question: "{state['question']}"{feedback}"""
        draft = llm.invoke(prompt).content

    return {"draft_reply": draft, "retry_count": state.get("retry_count", 0) + 1}


NUMBER_PATTERN = re.compile(r"\b\d[\d,]*\b")


def grounding_check_node(state: MentorshipState) -> dict:
    draft = state["draft_reply"]
    profile = state["profile"]
    evidence_blob = " ".join(e.claim for e in profile.evidence_log).lower()

    issues = []
    for number in set(NUMBER_PATTERN.findall(draft)):
        if len(number) > 2 and number not in evidence_blob:
            issues.append(f"Number '{number}' in the reply isn't backed by anything in the evidence log")

    return {"grounding_issues": issues}


def should_retry(state: MentorshipState) -> str:
    if state.get("grounding_issues") and state.get("retry_count", 0) < MAX_RETRIES:
        return "retry"
    return "done"
