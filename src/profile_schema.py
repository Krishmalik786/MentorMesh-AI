"""
The Startup Profile schema — the structured shape every startup gets
normalized into, regardless of which of the 4 links it came from.

Design note: every substantive claim in the profile should trace back to an
Evidence entry. Without that, the mentorship chat (Phase 3) can only give
generic advice — with it, it can say "your README claims X but your last
commit was 4 months ago" instead of "keep improving your product."
"""

from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class SourceType(str, Enum):
    GITHUB = "github"
    WEBSITE = "website"
    PITCH_DECK = "pitch_deck"
    SOCIAL = "social"


class Evidence(BaseModel):
    """A single fact, tied back to where it came from, so mentorship can cite it."""

    source: SourceType
    claim: str
    detail: str | None = None


class TechnicalProfile(BaseModel):
    languages: list[str] = Field(default_factory=list)
    frameworks: list[str] = Field(default_factory=list)
    last_commit_date: datetime | None = None
    commit_frequency_note: str | None = None  # e.g. "12 commits in last 30 days"
    contributor_count: int | None = None
    has_tests: bool | None = None
    has_ci: bool | None = None
    readme_summary: str | None = None


class ProductProfile(BaseModel):
    value_proposition: str | None = None
    target_market: str | None = None
    key_features: list[str] = Field(default_factory=list)
    pricing_model_note: str | None = None


class PitchProfile(BaseModel):
    problem_statement: str | None = None
    solution_summary: str | None = None
    business_model: str | None = None
    traction_claims: list[str] = Field(default_factory=list)
    funding_ask: str | None = None
    team_notes: str | None = None


class SocialProfile(BaseModel):
    platforms: list[str] = Field(default_factory=list)
    follower_counts: dict[str, int] = Field(default_factory=dict)
    posting_cadence_note: str | None = None
    content_themes: list[str] = Field(default_factory=list)


class StartupProfile(BaseModel):
    company_name: str | None = None
    one_line_summary: str | None = None

    source_links: dict[SourceType, str] = Field(default_factory=dict)
    unreachable_sources: list[SourceType] = Field(default_factory=list)

    technical: TechnicalProfile = Field(default_factory=TechnicalProfile)
    product: ProductProfile = Field(default_factory=ProductProfile)
    pitch: PitchProfile = Field(default_factory=PitchProfile)
    social: SocialProfile = Field(default_factory=SocialProfile)

    evidence_log: list[Evidence] = Field(default_factory=list)

    created_at: datetime | None = None
