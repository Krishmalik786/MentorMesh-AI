"""
Shared state for the Phase 3 mentorship graph.

specialist_responses uses a custom merge function because multiple
specialist nodes can run in parallel (via LangGraph's Send fan-out) and
each writes its own entry — without a merge reducer, parallel writes to the
same key would clobber each other instead of combining.
"""

from typing import Annotated, Optional, TypedDict

from src.profile_schema import StartupProfile


def _merge_dicts(a: dict, b: dict) -> dict:
    return {**a, **b}


class MentorshipState(TypedDict):
    profile: StartupProfile
    question: str

    specialists_to_run: list[str]
    specialist_responses: Annotated[dict[str, str], _merge_dicts]

    draft_reply: Optional[str]
    grounding_issues: list[str]
    retry_count: int
