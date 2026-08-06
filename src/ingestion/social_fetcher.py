"""
Social media fetcher — reads whatever public preview data a social profile
link exposes, without logging in.

Scope: Twitter/X, Instagram, LinkedIn, and most other platforms wall off
full profile data (post history, exact follower counts) behind a login.
What they do keep public are Open Graph tags — the same metadata that
makes link previews work in iMessage/Slack/etc. This fetcher reads only
that: name/title, a short bio/description, and (best-effort) a follower
count if the platform happens to embed it in that description text.
Nothing is guessed — if a field isn't present, it's left empty.
"""

import re

import requests
from bs4 import BeautifulSoup

from src.ingestion.base import FetchResult
from src.profile_schema import Evidence, SourceType

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; StartupCopilotBot/0.1)"}
FOLLOWER_PATTERN = re.compile(r"([\d.,]+\s?[KMB]?)\s+Followers", re.IGNORECASE)


def _meta_content(soup: BeautifulSoup, *, property_: str | None = None, name: str | None = None) -> str | None:
    attrs = {"property": property_} if property_ else {"name": name}
    tag = soup.find("meta", attrs=attrs)
    return tag["content"].strip() if tag and tag.get("content") else None


def fetch_social(url: str) -> FetchResult:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
    except requests.RequestException as e:
        return FetchResult(reachable=False, error=f"Could not reach {url}: {e}")

    if resp.status_code != 200:
        return FetchResult(reachable=False, error=f"{url} returned status {resp.status_code}")

    soup = BeautifulSoup(resp.text, "html.parser")

    title = (
        _meta_content(soup, property_="og:title")
        or _meta_content(soup, name="twitter:title")
        or (soup.title.string.strip() if soup.title and soup.title.string else None)
    )
    description = (
        _meta_content(soup, property_="og:description")
        or _meta_content(soup, name="twitter:description")
        or _meta_content(soup, name="description")
    )
    site_name = _meta_content(soup, property_="og:site_name")

    follower_count_text = None
    if description:
        match = FOLLOWER_PATTERN.search(description)
        if match:
            follower_count_text = match.group(1)

    raw_data = {
        "url": url,
        "platform": site_name,
        "title": title,
        "description": description,
        "follower_count_text": follower_count_text,
    }

    evidence = []
    if title:
        evidence.append(Evidence(source=SourceType.SOCIAL, claim=f'Profile title/name: "{title}"'))
    if description:
        evidence.append(Evidence(source=SourceType.SOCIAL, claim=f'Public bio/description: "{description}"'))
    if follower_count_text:
        evidence.append(
            Evidence(
                source=SourceType.SOCIAL,
                claim=f"Follower count (approx, from preview text): {follower_count_text}",
            )
        )
    if not title and not description:
        evidence.append(
            Evidence(
                source=SourceType.SOCIAL,
                claim="No public preview data found for this link (platform may require login to view)",
            )
        )

    return FetchResult(reachable=True, raw_data=raw_data, evidence=evidence)
