"""
Shared state that flows through the Phase 2 LangGraph graph.

LangGraph passes this dict-like object between nodes; each node reads what
it needs and returns a partial update that gets merged in.
"""

from typing import Optional, TypedDict

from src.profile_schema import Evidence, SourceType, StartupProfile
from src.synthesis.narrative_schema import SynthesizedNarrative


class SynthesisState(TypedDict):
    github_data: Optional[dict]
    website_data: Optional[dict]
    pitch_deck_data: Optional[dict]
    social_data: Optional[dict]

    collected_evidence: list[Evidence]
    unreachable_sources: list[SourceType]
    source_links: dict[SourceType, str]

    narrative: Optional[SynthesizedNarrative]
    profile: Optional[StartupProfile]
    validation_errors: list[str]
    retry_count: int
