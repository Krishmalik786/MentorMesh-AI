"""
Password hashing (bcrypt) and session tokens (JWT) for the API.

Sessions are stateless bearer tokens: the frontend sends
`Authorization: Bearer <token>`, we verify the signature + expiry and load
the user by id. No server-side session store needed.
"""

import os
import uuid
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.db import get_session
from src.models import User

JWT_ALGORITHM = "HS256"
JWT_EXPIRES_HOURS = 24 * 7

_bearer_scheme = HTTPBearer(auto_error=False)


def _jwt_secret() -> str:
    secret = os.environ.get("JWT_SECRET")
    if not secret:
        raise RuntimeError("JWT_SECRET is not set")
    return secret


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def create_token(user_id: uuid.UUID) -> str:
    payload = {
        "sub": str(user_id),
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRES_HOURS),
    }
    return jwt.encode(payload, _jwt_secret(), algorithm=JWT_ALGORITHM)


def _decode_token(token: str) -> uuid.UUID:
    try:
        payload = jwt.decode(token, _jwt_secret(), algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError as e:
        raise HTTPException(401, "Invalid or expired session") from e
    return uuid.UUID(payload["sub"])


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> User:
    if credentials is None:
        raise HTTPException(401, "Missing Authorization header")

    user_id = _decode_token(credentials.credentials)
    with get_session() as session:
        user = session.get(User, user_id)
        if user is None:
            raise HTTPException(401, "Unknown user")
        session.expunge(user)
    return user
