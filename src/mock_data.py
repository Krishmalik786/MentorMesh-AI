"""
A fully-populated mock StartupProfile for a fictional startup ("Loopwise").

Purpose: real fetched profiles (like our FastAPI test) are missing whole
sections — there's no real pitch deck for an open-source project, so
`pitch` stays empty. This mock exercises every field in the schema at once,
which makes it useful both for fast Streamlit UI iteration (no waiting on
real scraping + LLM calls) and as a clean example of what a "complete"
profile actually looks like.

Run directly to save it into the same storage the API uses, under a fixed
"demo" id: python -m src.mock_data
"""

from datetime import datetime, timezone

from src.api import storage
from src.profile_schema import (
    Evidence,
    PitchProfile,
    ProductProfile,
    SocialProfile,
    SourceType,
    StartupProfile,
    TechnicalProfile,
)

DEMO_PROFILE_ID = "demo"


def build_mock_profile() -> StartupProfile:
    return StartupProfile(
        company_name="Loopwise",
        one_line_summary="AI agents that automate multi-step backend workflows for small engineering teams.",
        source_links={
            SourceType.GITHUB: "https://github.com/loopwise-hq/loopwise",
            SourceType.WEBSITE: "https://loopwise.dev",
            SourceType.PITCH_DECK: "https://loopwise.dev/seed-deck.pdf",
            SourceType.SOCIAL: "https://twitter.com/loopwisehq",
        },
        unreachable_sources=[],
        technical=TechnicalProfile(
            languages=["Python", "TypeScript"],
            frameworks=["FastAPI", "React"],
            last_commit_date=datetime(2026, 8, 4, tzinfo=timezone.utc),
            commit_frequency_note="34 commits in the last 30 days",
            contributor_count=4,
            has_tests=True,
            has_ci=True,
            readme_summary="Loopwise is an open-core workflow automation engine — the public repo "
            "contains the SDK and the self-hosted runner.",
        ),
        product=ProductProfile(
            value_proposition="Loopwise lets engineering teams automate multi-step backend workflows "
            "(data syncs, approvals, alerts) without writing custom glue code.",
            target_market="Series A-B B2B SaaS companies with 10-50 person engineering teams",
            key_features=[
                "Visual workflow builder",
                "Native Slack, GitHub, and Postgres connectors",
                "Self-hostable runner",
                "Built-in retry logic and audit logging",
            ],
            pricing_model_note="Usage-based pricing per workflow run; free tier up to 1,000 runs/month",
        ),
        pitch=PitchProfile(
            problem_statement="Engineering teams spend significant time writing and maintaining custom "
            "scripts to glue internal tools together — these break silently and are hard to audit.",
            solution_summary="A visual, versioned workflow engine with native integrations and built-in "
            "observability, deployable self-hosted or managed.",
            business_model="Usage-based SaaS with an open-core self-hosted tier",
            traction_claims=[
                "12 paying pilot customers",
                "$18K MRR",
                "3.2x quarter-over-quarter growth in workflow runs",
            ],
            funding_ask="$1.5M seed to expand the integrations library and hire 2 engineers",
            team_notes="Founding team of 2 ex-Stripe infrastructure engineers",
        ),
        social=SocialProfile(
            platforms=["X (formerly Twitter)"],
            follower_counts={"X (formerly Twitter)": 2400},
            posting_cadence_note="Weekly build-in-public updates",
            content_themes=["workflow automation", "developer tools", "building in public"],
        ),
        evidence_log=[
            Evidence(source=SourceType.GITHUB, claim="34 commits in the last 30 days"),
            Evidence(source=SourceType.GITHUB, claim="Has CI configuration (.github/workflows)"),
            Evidence(source=SourceType.GITHUB, claim="Has visible tests directory"),
            Evidence(source=SourceType.GITHUB, claim="4 contributor(s) on record"),
            Evidence(
                source=SourceType.WEBSITE,
                claim='Meta description: "Loopwise automates backend workflows for engineering teams"',
            ),
            Evidence(source=SourceType.WEBSITE, claim="Extracted 640 words of main page content"),
            Evidence(
                source=SourceType.PITCH_DECK,
                claim="Deck page 4 states 12 paying pilot customers and $18K MRR",
            ),
            Evidence(source=SourceType.PITCH_DECK, claim="Deck page 9 states funding ask of $1.5M seed"),
            Evidence(
                source=SourceType.SOCIAL,
                claim='Public bio/description: "Building the workflow layer for modern eng teams"',
            ),
            Evidence(source=SourceType.SOCIAL, claim="Follower count (approx, from preview text): 2.4K"),
        ],
        created_at=datetime.now(timezone.utc),
    )


if __name__ == "__main__":
    profile = build_mock_profile()
    storage.set_status(DEMO_PROFILE_ID, "done", profile=profile)
    print(f"Saved mock profile under id='{DEMO_PROFILE_ID}'")
