"""
Website fetcher — reads a startup's homepage and produces raw signal for
the ProductProfile section of the StartupProfile.

Same shape as github_fetcher.py: one function, fetch_website(url), same
FetchResult contract. Uses trafilatura to strip navigation/footer/ad
boilerplate and keep just the main readable content — a plain HTML parse
(BeautifulSoup alone) would include a lot of noise a page's actual pitch.

Fallback: some sites render their real content with JavaScript, so the raw
HTML we download is nearly empty. If the fast path comes back with too few
words, we retry with Playwright — a real (headless) browser that runs the
page's JavaScript before we read it. Slower, so it's only used when needed.
"""

import requests
import trafilatura
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

from src.ingestion.base import FetchResult
from src.profile_schema import Evidence, SourceType

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; StartupCopilotBot/0.1)"}
MIN_WORDS_BEFORE_FALLBACK = 40


def _parse_html(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")

    title = soup.title.string.strip() if soup.title and soup.title.string else None

    meta_description = None
    meta_tag = soup.find("meta", attrs={"name": "description"})
    if meta_tag and meta_tag.get("content"):
        meta_description = meta_tag["content"].strip()

    main_text = trafilatura.extract(html, include_comments=False, include_tables=False)

    return {
        "title": title,
        "meta_description": meta_description,
        "main_text": main_text,
        "word_count": len(main_text.split()) if main_text else 0,
    }


def _render_with_browser(url: str) -> str | None:
    """Open the page in a real (headless) browser and return the rendered HTML."""
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(user_agent=HEADERS["User-Agent"])
            page.goto(url, timeout=15000, wait_until="networkidle")
            html = page.content()
            browser.close()
            return html
    except Exception:
        return None


def fetch_website(url: str) -> FetchResult:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
    except requests.RequestException as e:
        return FetchResult(reachable=False, error=f"Could not reach {url}: {e}")

    if resp.status_code != 200:
        return FetchResult(reachable=False, error=f"{url} returned status {resp.status_code}")

    parsed = _parse_html(resp.text)
    used_browser_fallback = False

    if parsed["word_count"] < MIN_WORDS_BEFORE_FALLBACK:
        rendered_html = _render_with_browser(url)
        if rendered_html:
            rendered_parsed = _parse_html(rendered_html)
            if rendered_parsed["word_count"] > parsed["word_count"]:
                parsed = rendered_parsed
                used_browser_fallback = True

    raw_data = {"url": url, **parsed}

    evidence = []
    if parsed["title"]:
        evidence.append(Evidence(source=SourceType.WEBSITE, claim=f"Page title: \"{parsed['title']}\""))
    if parsed["meta_description"]:
        evidence.append(
            Evidence(source=SourceType.WEBSITE, claim=f"Meta description: \"{parsed['meta_description']}\"")
        )
    if parsed["main_text"]:
        note = " (required rendering JavaScript to read)" if used_browser_fallback else ""
        evidence.append(
            Evidence(
                source=SourceType.WEBSITE,
                claim=f"Extracted {parsed['word_count']} words of main page content{note}",
            )
        )
    else:
        evidence.append(
            Evidence(
                source=SourceType.WEBSITE,
                claim="Could not extract readable main content from this page, even after rendering JavaScript",
            )
        )

    return FetchResult(reachable=True, raw_data=raw_data, evidence=evidence)
