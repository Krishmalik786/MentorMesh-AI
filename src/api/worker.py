"""
Runs profile building in a background thread so POST /profile can return
immediately instead of blocking the HTTP request for the ~30-60s it takes
to fetch and synthesize. A thread is enough here — this is single-user, not
a job queue serving many concurrent requests.
"""

import threading

from src.api import storage
from src.pipeline import build_profile


def start_profile_build(profile_id: str, **urls) -> None:
    thread = threading.Thread(target=_run, args=(profile_id,), kwargs=urls, daemon=True)
    thread.start()


def _run(profile_id: str, **urls) -> None:
    try:
        profile, _validation_errors = build_profile(
            **urls,
            on_status=lambda stage: storage.set_status(profile_id, stage),
        )
        storage.set_status(profile_id, "done", profile=profile)
    except Exception as e:
        storage.set_status(profile_id, "failed", error=str(e))
