"""
Narrower schema for what the LLM actually generates in Phase 2.

Deliberately excludes anything already known deterministically from the
fetchers (commit counts, follower counts, has_tests, has_ci, etc.) — those
are copied straight from raw fetcher data in code (see nodes.py), with zero
LLM involvement, so they can never be hallucinated. The LLM only fills in
fields that genuinely require reading comprehension: summarizing, judging
positioning, interpreting a pitch's narrative.
"""

from pydantic import BaseModel, Field


class SynthesizedNarrative(BaseModel):
    company_name: str | None = None
    one_line_summary: str | None = None

    readme_summary: str | None = None

    value_proposition: str | None = None
    target_market: str | None = None
    key_features: list[str] = Field(default_factory=list)
    pricing_model_note: str | None = None

    problem_statement: str | None = None
    solution_summary: str | None = None
    business_model: str | None = None
    traction_claims: list[str] = Field(default_factory=list)
    funding_ask: str | None = None
    team_notes: str | None = None

    content_themes: list[str] = Field(default_factory=list)
    posting_cadence_note: str | None = None
