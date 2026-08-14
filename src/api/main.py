"""
Minimal FastAPI backend wrapping the Phase 1-3 pipeline.

POST /auth/signup   -> create a user account
POST /auth/login    -> exchange email+password for a bearer token
GET  /auth/me        -> the current user, given a bearer token
POST /profile        -> kicks off building a profile in the background, returns right away (auth required)
GET  /profile/{id}   -> current progress, and the profile once status is "done" (public)
POST /chat           -> ask a question about a completed profile (auth required)

Run with: uvicorn src.api.main:app --reload
"""

import os
import uuid

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError

from src.api import storage
from src.api.auth import create_token, get_current_user, hash_password, verify_password
from src.api.worker import start_profile_build
from src.db import get_session
from src.mentorship.graph import answer_question
from src.mock_data import DEMO_PROFILE_ID, build_mock_profile
from src.models import User

app = FastAPI(title="Startup Copilot API")

_allowed_origins = [o.strip() for o in os.environ.get("FRONTEND_ORIGIN", "http://localhost:3000").split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SignupRequest(BaseModel):
    email: str
    password: str
    name: str | None = None


class LoginRequest(BaseModel):
    email: str
    password: str


class CreateProfileRequest(BaseModel):
    github_url: str | None = None
    website_url: str | None = None
    pitch_deck_url: str | None = None
    social_url: str | None = None


class ChatRequest(BaseModel):
    profile_id: str
    question: str


@app.post("/auth/signup")
def signup(req: SignupRequest):
    user = User(id=uuid.uuid4(), email=req.email.lower(), password_hash=hash_password(req.password), name=req.name)
    with get_session() as session:
        session.add(user)
        try:
            session.commit()
        except IntegrityError as e:
            raise HTTPException(400, "An account with that email already exists") from e
        user_id = user.id

    return {"access_token": create_token(user_id), "token_type": "bearer"}


@app.post("/auth/login")
def login(req: LoginRequest):
    with get_session() as session:
        user = session.query(User).filter(User.email == req.email.lower()).one_or_none()
        if user is None or not verify_password(req.password, user.password_hash):
            raise HTTPException(401, "Incorrect email or password")
        user_id = user.id

    return {"access_token": create_token(user_id), "token_type": "bearer"}


@app.get("/auth/me")
def me(current_user: User = Depends(get_current_user)):
    return {"id": str(current_user.id), "email": current_user.email, "name": current_user.name}


@app.post("/profile")
def create_profile(req: CreateProfileRequest, current_user: User = Depends(get_current_user)):
    if not any([req.github_url, req.website_url, req.pitch_deck_url, req.social_url]):
        raise HTTPException(400, "Provide at least one link")

    profile_id = str(uuid.uuid4())
    storage.set_status(profile_id, "queued", owner_user_id=current_user.id)
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

    # The demo profile is generated data, not something that ships with the
    # deployment (its source, mock_data.py, does) — build it on first request
    # instead of requiring a manual step on whatever server this runs on.
    if entry is None and profile_id == DEMO_PROFILE_ID:
        storage.set_status(DEMO_PROFILE_ID, "done", profile=build_mock_profile())
        entry = storage.get_status(profile_id)

    if entry is None:
        raise HTTPException(404, "Unknown profile_id")
    return {
        "status": entry["status"],
        "error": entry.get("error"),
        "profile": entry["profile"].model_dump() if entry.get("profile") else None,
    }


@app.post("/chat")
def chat(req: ChatRequest, current_user: User = Depends(get_current_user)):
    entry = storage.get_status(req.profile_id)
    if entry is None or entry["status"] != "done" or entry.get("profile") is None:
        raise HTTPException(400, "This profile isn't ready yet, or doesn't exist")

    return answer_question(entry["profile"], req.question)
