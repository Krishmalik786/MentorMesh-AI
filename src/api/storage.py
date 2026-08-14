"""
Storage for the API: profiles live in the `startup_profiles` table (Neon
Postgres), keyed by profile_id.

`set_status` doubles as both "create" (first call for a given profile_id,
optionally passing owner_user_id) and "update" (every later call, as the
pipeline progresses through stages and finally reaches "done"/"failed").
"""

import uuid

from src.db import get_session
from src.models import StartupProfileRecord
from src.profile_schema import StartupProfile


def set_status(
    profile_id: str,
    status: str,
    profile: StartupProfile | None = None,
    error: str | None = None,
    owner_user_id: uuid.UUID | None = None,
) -> None:
    with get_session() as session:
        record = session.get(StartupProfileRecord, profile_id)
        if record is None:
            record = StartupProfileRecord(id=profile_id, owner_user_id=owner_user_id)
            session.add(record)

        record.status = status
        record.error = error
        if profile is not None:
            record.profile_data = profile.model_dump(mode="json")
        session.commit()


def get_status(profile_id: str) -> dict | None:
    with get_session() as session:
        record = session.get(StartupProfileRecord, profile_id)
        if record is None:
            return None
        return {
            "status": record.status,
            "error": record.error,
            "profile": StartupProfile.model_validate(record.profile_data)
            if record.profile_data
            else None,
        }
