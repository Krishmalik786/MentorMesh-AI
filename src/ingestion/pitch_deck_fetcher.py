"""
Pitch deck fetcher — reads a direct PDF link and produces raw signal for
the PitchProfile section of the StartupProfile.

Scope note: this handles direct PDF links only. DocSend / Google Slides /
Canva share links need a real browser session (and often block scraping
outright) — same category of problem as social media, worth a separate
decision rather than folding in here.

Extracts text per page with pypdf. Pitch decks are often image-heavy
(charts, mockups, big text on a background image) — a page with very
little extractable text is flagged as "likely image-heavy" rather than
silently treated as empty. Whether to add actual image/vision analysis of
those slides is a Phase 2 decision, not this one.
"""

import io

import requests
from pypdf import PdfReader

from src.ingestion.base import FetchResult
from src.profile_schema import Evidence, SourceType

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; StartupCopilotBot/0.1)"}
MIN_WORDS_PER_PAGE = 10


def fetch_pitch_deck(url: str) -> FetchResult:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
    except requests.RequestException as e:
        return FetchResult(reachable=False, error=f"Could not reach {url}: {e}")

    if resp.status_code != 200:
        return FetchResult(reachable=False, error=f"{url} returned status {resp.status_code}")

    content_type = resp.headers.get("Content-Type", "")
    is_pdf = "application/pdf" in content_type or resp.content[:4] == b"%PDF"
    if not is_pdf:
        return FetchResult(
            reachable=False,
            error=(
                f"{url} doesn't look like a direct PDF (Content-Type: {content_type or 'unknown'}). "
                "DocSend/Google Slides/Canva links aren't supported yet — need a direct .pdf link."
            ),
        )

    try:
        reader = PdfReader(io.BytesIO(resp.content))
    except Exception as e:
        return FetchResult(reachable=False, error=f"Could not parse PDF from {url}: {e}")

    pages_text = []
    image_heavy_pages = []
    for i, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()
        pages_text.append(text)
        if len(text.split()) < MIN_WORDS_PER_PAGE:
            image_heavy_pages.append(i)

    full_text = "\n\n".join(t for t in pages_text if t)
    total_word_count = sum(len(t.split()) for t in pages_text)

    raw_data = {
        "url": url,
        "page_count": len(reader.pages),
        "pages_text": pages_text,
        "full_text": full_text,
        "total_word_count": total_word_count,
        "image_heavy_pages": image_heavy_pages,
    }

    evidence = [
        Evidence(source=SourceType.PITCH_DECK, claim=f"Deck has {len(reader.pages)} page(s)"),
        Evidence(
            source=SourceType.PITCH_DECK,
            claim=f"Extracted {total_word_count} words of text across the deck",
        ),
    ]
    if image_heavy_pages:
        evidence.append(
            Evidence(
                source=SourceType.PITCH_DECK,
                claim=(
                    f"{len(image_heavy_pages)} page(s) had very little extractable text "
                    f"(likely image/chart-heavy): pages {image_heavy_pages}"
                ),
            )
        )

    return FetchResult(reachable=True, raw_data=raw_data, evidence=evidence)
