"""
Runs profile building in a background thread so POST /profile can return
immediately instead of blocking the HTTP request for the ~30-60s it takes
to fetch and synthesize. A thread is enough here — this is single-user, not
a job queue serving many concurrent requests.
"""

import threading
import traceback

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
        # Print the full traceback so it actually shows up in server logs —
        # without this, a hosting platform's log stream shows nothing at
        # all for a failure here, since we only store str(e) for the API.
        print(f"[profile_build:{profile_id}] failed:")
        traceback.print_exc()
        storage.set_status(profile_id, "failed", error=str(e))
