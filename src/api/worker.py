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
        # Print the full traceback so it actually shows up in server logs.
        print(f"[profile_build:{profile_id}] failed:")
        traceback.print_exc()

        # Also surface the *chained* root cause directly in the API's error
        # field (e.g. openai.APIConnectionError wraps the real httpx-level
        # error via `raise ... from err`) — reading it here is far easier
        # than hunting through a hosting platform's log scrollback.
        error_parts = [f"{type(e).__name__}: {e}"]
        cause = e.__cause__
        while cause is not None:
            error_parts.append(f"caused by {type(cause).__name__}: {cause}")
            cause = cause.__cause__

        storage.set_status(profile_id, "failed", error=" | ".join(error_parts))
