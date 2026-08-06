"""
GitHub fetcher — reads a public repo and produces raw signal for the
TechnicalProfile section of the StartupProfile.

Uses the GitHub REST API directly (no SDK) so the HTTP calls are visible.
Unauthenticated requests are capped at 60/hour per IP, which is plenty for
one repo (~5 calls). Set GITHUB_TOKEN in a .env file to raise that to 5000/hour
if you're testing against many repos.
"""

import base64
import os
import re
from datetime import datetime, timedelta, timezone

import requests
from dotenv import load_dotenv

from src.ingestion.base import FetchResult
from src.profile_schema import Evidence, SourceType

load_dotenv()

API_BASE = "https://api.github.com"


def _headers() -> dict:
    headers = {"Accept": "application/vnd.github+json"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _parse_owner_repo(repo_url: str) -> tuple[str, str] | None:
    match = re.search(r"github\.com/([^/]+)/([^/]+?)(?:\.git)?/?$", repo_url.strip())
    if not match:
        return None
    return match.group(1), match.group(2)


def fetch_github(repo_url: str) -> FetchResult:
    parsed = _parse_owner_repo(repo_url)
    if not parsed:
        return FetchResult(reachable=False, error=f"Could not parse a GitHub owner/repo from: {repo_url}")

    owner, repo = parsed
    headers = _headers()
    base = f"{API_BASE}/repos/{owner}/{repo}"

    repo_resp = requests.get(base, headers=headers, timeout=10)
    if repo_resp.status_code != 200:
        return FetchResult(
            reachable=False,
            error=f"GitHub API returned {repo_resp.status_code} for {owner}/{repo}: {repo_resp.text[:200]}",
        )
    repo_data = repo_resp.json()

    languages_data = requests.get(f"{base}/languages", headers=headers, timeout=10).json()

    readme_resp = requests.get(f"{base}/readme", headers=headers, timeout=10)
    readme_text = None
    if readme_resp.status_code == 200:
        content = readme_resp.json().get("content", "")
        try:
            readme_text = base64.b64decode(content).decode("utf-8", errors="ignore")
        except Exception:
            readme_text = None

    contents_resp = requests.get(f"{base}/contents", headers=headers, timeout=10)
    root_entries = [e["name"] for e in contents_resp.json()] if contents_resp.status_code == 200 else []

    workflows_resp = requests.get(f"{base}/contents/.github/workflows", headers=headers, timeout=10)
    has_ci = workflows_resp.status_code == 200

    test_dir_names = {"tests", "test", "__tests__", "spec"}
    has_tests = any(name.lower() in test_dir_names for name in root_entries)

    since = (datetime.now(timezone.utc) - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ")
    recent_commits_resp = requests.get(
        f"{base}/commits", headers=headers, params={"since": since, "per_page": 100}, timeout=10
    )
    recent_commit_count = len(recent_commits_resp.json()) if recent_commits_resp.status_code == 200 else None

    contributors_resp = requests.get(
        f"{base}/contributors", headers=headers, params={"per_page": 100, "anon": "true"}, timeout=10
    )
    contributor_count = len(contributors_resp.json()) if contributors_resp.status_code == 200 else None

    raw_data = {
        "name": repo_data.get("name"),
        "description": repo_data.get("description"),
        "stargazers_count": repo_data.get("stargazers_count"),
        "pushed_at": repo_data.get("pushed_at"),
        "languages": list(languages_data.keys()) if isinstance(languages_data, dict) else [],
        "readme_text": readme_text,
        "has_ci": has_ci,
        "has_tests": has_tests,
        "recent_commit_count_30d": recent_commit_count,
        "contributor_count": contributor_count,
    }

    evidence = []
    if repo_data.get("pushed_at"):
        evidence.append(
            Evidence(
                source=SourceType.GITHUB,
                claim=f"Repo last pushed to on {repo_data['pushed_at']}",
            )
        )
    if recent_commit_count is not None:
        evidence.append(
            Evidence(
                source=SourceType.GITHUB,
                claim=f"{recent_commit_count} commits in the last 30 days",
            )
        )
    evidence.append(
        Evidence(
            source=SourceType.GITHUB,
            claim=f"{'Has' if has_ci else 'No'} CI configuration (.github/workflows)",
        )
    )
    evidence.append(
        Evidence(
            source=SourceType.GITHUB,
            claim=f"{'Has' if has_tests else 'No'} visible tests directory",
        )
    )
    if contributor_count is not None:
        evidence.append(
            Evidence(source=SourceType.GITHUB, claim=f"{contributor_count} contributor(s) on record")
        )

    return FetchResult(reachable=True, raw_data=raw_data, evidence=evidence)
