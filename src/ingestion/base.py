"""
Shared contract every fetcher implements.

Why this exists: each fetcher (GitHub, website, deck, social) is a fully
independent module — same input/output shape, no shared state. That's what
makes them swappable/parallelizable later, and it's the exact boundary
we'd wrap as a separate "agent" if/when each fetcher gets its own LLM
reasoning step (e.g. an LLM summarizing a README vs. just regexing it).

Every fetch_*(link) function returns a FetchResult:
- reachable=False + error set if the link couldn't be read at all
- raw_data holds whatever the fetcher pulled, in its own shape (Phase 2's
  synthesis step is what maps this into the shared StartupProfile)
- evidence is already in the shared Evidence format, since fetchers know
  best what they found and why it matters
"""

from dataclasses import dataclass, field

from src.profile_schema import Evidence


@dataclass
class FetchResult:
    reachable: bool
    raw_data: dict = field(default_factory=dict)
    evidence: list[Evidence] = field(default_factory=list)
    error: str | None = None
