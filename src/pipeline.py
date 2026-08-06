"""
End-to-end pipeline: Phase 1 ingestion -> Phase 2 synthesis.

Runs whichever fetchers have a link provided, collects their raw data and
evidence, then runs it all through the synthesis graph to produce one
StartupProfile.
"""

from typing import Callable, Optional

from src.ingestion.github_fetcher import fetch_github
from src.ingestion.pitch_deck_fetcher import fetch_pitch_deck
from src.ingestion.social_fetcher import fetch_social
from src.ingestion.website_fetcher import fetch_website
from src.profile_schema import SourceType, StartupProfile
from src.synthesis.graph import build_synthesis_graph

_FETCHERS = {
    SourceType.GITHUB: fetch_github,
    SourceType.WEBSITE: fetch_website,
    SourceType.PITCH_DECK: fetch_pitch_deck,
    SourceType.SOCIAL: fetch_social,
}


def build_profile(
    *,
    github_url: str | None = None,
    website_url: str | None = None,
    pitch_deck_url: str | None = None,
    social_url: str | None = None,
    on_status: Optional[Callable[[str], None]] = None,
) -> tuple[StartupProfile, list[str]]:
    """on_status, if given, is called with a short stage name (e.g.
    "fetching_github", "synthesizing") as the pipeline progresses — lets a
    caller (like the API's background worker) report live progress instead
    of the caller just blocking until everything is done."""

    def report(stage: str) -> None:
        if on_status:
            on_status(stage)

    urls = {
        SourceType.GITHUB: github_url,
        SourceType.WEBSITE: website_url,
        SourceType.PITCH_DECK: pitch_deck_url,
        SourceType.SOCIAL: social_url,
    }

    raw_data: dict[str, dict] = {}
    collected_evidence = []
    unreachable_sources = []
    source_links = {}
    fetch_errors = {}

    for source, url in urls.items():
        if not url:
            continue
        report(f"fetching_{source.value}")
        source_links[source] = url
        result = _FETCHERS[source](url)
        if result.reachable:
            raw_data[source.value] = result.raw_data
            collected_evidence.extend(result.evidence)
        else:
            unreachable_sources.append(source)
            fetch_errors[source.value] = result.error

    report("synthesizing")
    graph = build_synthesis_graph()
    final_state = graph.invoke(
        {
            "github_data": raw_data.get("github"),
            "website_data": raw_data.get("website"),
            "pitch_deck_data": raw_data.get("pitch_deck"),
            "social_data": raw_data.get("social"),
            "collected_evidence": collected_evidence,
            "unreachable_sources": unreachable_sources,
            "source_links": source_links,
            "retry_count": 0,
            "validation_errors": [],
        }
    )

    if fetch_errors:
        print("Sources that could not be fetched:", fetch_errors)

    return final_state["profile"], final_state["validation_errors"]
