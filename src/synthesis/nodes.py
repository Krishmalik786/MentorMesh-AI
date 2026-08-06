"""
Phase 2 synthesis graph nodes.

synthesize — LLM fills in only the interpretive fields (see narrative_schema.py).
assemble   — plain code merges that with deterministic facts pulled directly
             from raw fetcher data, and attaches the fetchers' own evidence
             log untouched. This is what makes deterministic facts
             (commit counts, follower counts, etc.) immune to hallucination:
             the LLM never touches them at all.
validate   — checks the assembled profile for completeness, and spot-checks
             that any number mentioned in the LLM's narrative text actually
             appears somewhere in the raw source data (catches invented stats).
"""

import re

from src.profile_schema import (
    PitchProfile,
    ProductProfile,
    SocialProfile,
    StartupProfile,
    TechnicalProfile,
)
from src.llm_client import get_llm
from src.synthesis.narrative_schema import SynthesizedNarrative
from src.synthesis.state import SynthesisState

MAX_RETRIES = 2

SYSTEM_PROMPT = """You are reading raw data gathered about a startup (from its \
GitHub repo, website, pitch deck, and/or social media) and summarizing it.

Only state things that are actually present in the raw data below. If \
something isn't there, leave that field null/empty rather than guessing or \
inferring. Do not invent numbers, claims, or facts that aren't in the data."""


def _format_raw_data(state: SynthesisState) -> str:
    parts = []
    if state.get("github_data"):
        parts.append(f"=== GITHUB ===\n{state['github_data']}")
    if state.get("website_data"):
        parts.append(f"=== WEBSITE ===\n{state['website_data']}")
    if state.get("pitch_deck_data"):
        parts.append(f"=== PITCH DECK ===\n{state['pitch_deck_data']}")
    if state.get("social_data"):
        parts.append(f"=== SOCIAL ===\n{state['social_data']}")
    return "\n\n".join(parts) if parts else "(no data was successfully fetched)"


def synthesize_node(state: SynthesisState) -> dict:
    # Higher max_tokens than the client default — this model reasons
    # internally before answering, and synthesis output is much longer
    # than a one-line reply.
    llm = get_llm(max_tokens=4096)
    structured_llm = llm.with_structured_output(SynthesizedNarrative)

    prompt = f"{SYSTEM_PROMPT}\n\nRaw data:\n{_format_raw_data(state)}"
    if state.get("validation_errors"):
        prompt += "\n\nThe previous attempt had these problems — fix them:\n" + "\n".join(
            f"- {e}" for e in state["validation_errors"]
        )

    narrative = structured_llm.invoke(prompt)
    return {"narrative": narrative, "retry_count": state.get("retry_count", 0) + 1}


def _parse_follower_count(text: str) -> int:
    text = text.strip().upper().replace(",", "")
    multiplier = 1
    if text.endswith("K"):
        multiplier, text = 1_000, text[:-1]
    elif text.endswith("M"):
        multiplier, text = 1_000_000, text[:-1]
    elif text.endswith("B"):
        multiplier, text = 1_000_000_000, text[:-1]
    try:
        return int(float(text) * multiplier)
    except ValueError:
        return 0


def assemble_node(state: SynthesisState) -> dict:
    narrative = state["narrative"]
    gh = state.get("github_data") or {}
    social = state.get("social_data") or {}

    technical = TechnicalProfile(
        languages=gh.get("languages", []),
        last_commit_date=gh.get("pushed_at"),
        commit_frequency_note=(
            f"{gh['recent_commit_count_30d']} commits in the last 30 days"
            if gh.get("recent_commit_count_30d") is not None
            else None
        ),
        contributor_count=gh.get("contributor_count"),
        has_tests=gh.get("has_tests"),
        has_ci=gh.get("has_ci"),
        readme_summary=narrative.readme_summary,
    )

    product = ProductProfile(
        value_proposition=narrative.value_proposition,
        target_market=narrative.target_market,
        key_features=narrative.key_features,
        pricing_model_note=narrative.pricing_model_note,
    )

    pitch = PitchProfile(
        problem_statement=narrative.problem_statement,
        solution_summary=narrative.solution_summary,
        business_model=narrative.business_model,
        traction_claims=narrative.traction_claims,
        funding_ask=narrative.funding_ask,
        team_notes=narrative.team_notes,
    )

    social_profile = SocialProfile(
        platforms=[social["platform"]] if social.get("platform") else [],
        follower_counts=(
            {social.get("platform") or "unknown": _parse_follower_count(social["follower_count_text"])}
            if social.get("follower_count_text")
            else {}
        ),
        posting_cadence_note=narrative.posting_cadence_note,
        content_themes=narrative.content_themes,
    )

    profile = StartupProfile(
        company_name=narrative.company_name,
        one_line_summary=narrative.one_line_summary,
        source_links=state.get("source_links", {}),
        unreachable_sources=state.get("unreachable_sources", []),
        technical=technical,
        product=product,
        pitch=pitch,
        social=social_profile,
        evidence_log=state.get("collected_evidence", []),
    )
    return {"profile": profile}


NUMBER_PATTERN = re.compile(r"\b\d[\d,]*\b")


def validate_node(state: SynthesisState) -> dict:
    profile = state["profile"]
    errors = []

    if not profile.company_name:
        errors.append("company_name is missing — check the raw data for a clear company/product name")
    if not profile.one_line_summary:
        errors.append("one_line_summary is missing")

    raw_text_blob = _format_raw_data(state)
    narrative_text = " ".join(
        str(v)
        for v in [
            profile.product.value_proposition,
            profile.pitch.problem_statement,
            profile.pitch.solution_summary,
            " ".join(profile.pitch.traction_claims),
        ]
        if v
    )
    for number in set(NUMBER_PATTERN.findall(narrative_text)):
        if len(number) > 2 and number not in raw_text_blob:
            errors.append(f"Number '{number}' appears in the summary but not in any raw source data")

    return {"validation_errors": errors}
