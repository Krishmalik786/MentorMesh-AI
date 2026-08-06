"""
Storage for the API: in-memory status while a profile is being built
(changes many times per second — no need to hit disk for that), plus
completed profiles saved to disk as JSON so they survive a server restart.

No database — this is proportionate to a single-user personal tool. If this
ever needed to serve multiple concurrent users, this file is exactly what'd
get replaced with a real DB; nothing else in the pipeline would need to change.
"""

import threading
from pathlib import Path

from src.profile_schema import StartupProfile

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "profiles"
DATA_DIR.mkdir(parents=True, exist_ok=True)

_lock = threading.Lock()
_status_store: dict[str, dict] = {}


def set_status(
    profile_id: str,
    status: str,
    profile: StartupProfile | None = None,
    error: str | None = None,
) -> None:
    with _lock:
        _status_store[profile_id] = {"status": status, "profile": profile, "error": error}
    if status == "done" and profile is not None:
        _save_to_disk(profile_id, profile)


def get_status(profile_id: str) -> dict | None:
    with _lock:
        entry = _status_store.get(profile_id)
    if entry is not None:
        return entry
    return _load_from_disk(profile_id)


def _save_to_disk(profile_id: str, profile: StartupProfile) -> None:
    path = DATA_DIR / f"{profile_id}.json"
    path.write_text(profile.model_dump_json(indent=2))


def _load_from_disk(profile_id: str) -> dict | None:
    path = DATA_DIR / f"{profile_id}.json"
    if not path.exists():
        return None
    profile = StartupProfile.model_validate_json(path.read_text())
    return {"status": "done", "profile": profile, "error": None}
