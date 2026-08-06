"""
Minimal FastAPI backend wrapping the Phase 1-3 pipeline.

POST /profile        -> kicks off building a profile in the background, returns right away
GET  /profile/{id}   -> current progress, and the profile once status is "done"
POST /chat           -> ask a question about a completed profile (Phase 3)

Run with: uvicorn src.api.main:app --reload
"""

import uuid

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.api import storage
from src.api.worker import start_profile_build
from src.mentorship.graph import answer_question

app = FastAPI(title="Startup Copilot API")


class CreateProfileRequest(BaseModel):
    github_url: str | None = None
    website_url: str | None = None
    pitch_deck_url: str | None = None
    social_url: str | None = None


class ChatRequest(BaseModel):
    profile_id: str
    question: str


@app.post("/profile")
def create_profile(req: CreateProfileRequest):
    if not any([req.github_url, req.website_url, req.pitch_deck_url, req.social_url]):
        raise HTTPException(400, "Provide at least one link")

    profile_id = str(uuid.uuid4())
    storage.set_status(profile_id, "queued")
    start_profile_build(
        profile_id,
        github_url=req.github_url,
        website_url=req.website_url,
        pitch_deck_url=req.pitch_deck_url,
        social_url=req.social_url,
    )
    return {"profile_id": profile_id, "status": "queued"}


@app.get("/profile/{profile_id}")
def get_profile(profile_id: str):
    entry = storage.get_status(profile_id)
    if entry is None:
        raise HTTPException(404, "Unknown profile_id")
    return {
        "status": entry["status"],
        "error": entry.get("error"),
        "profile": entry["profile"].model_dump() if entry.get("profile") else None,
    }


@app.post("/chat")
def chat(req: ChatRequest):
    entry = storage.get_status(req.profile_id)
    if entry is None or entry["status"] != "done" or entry.get("profile") is None:
        raise HTTPException(400, "This profile isn't ready yet, or doesn't exist")

    return answer_question(entry["profile"], req.question)
