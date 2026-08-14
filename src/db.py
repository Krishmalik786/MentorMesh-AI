"""
SQLAlchemy engine + session setup, pointed at Neon Postgres via DATABASE_URL.

Sync engine on purpose — the rest of the API (src/api/main.py route handlers,
src/api/worker.py's background thread) is sync, so this avoids mixing async
DB sessions into a sync codebase for no benefit at this scale.

The engine is built lazily rather than at import time: importing this module
must not require DATABASE_URL to be set yet. Alembic's env.py imports Base from
here to autogenerate migrations, and it loads the .env itself — an engine
created during import would blow up before that ever ran.
"""

import os
from functools import lru_cache

from dotenv import load_dotenv
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

load_dotenv()


class Base(DeclarativeBase):
    pass


def _database_url() -> str:
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is not set (expected a Neon Postgres connection string)")

    # Tolerate a value pasted with surrounding quotes from a dashboard or shell.
    url = url.strip().strip("'\"")

    # Neon hands out a bare `postgresql://` URL, which SQLAlchemy maps to
    # psycopg2. We install psycopg 3, so name the driver explicitly rather than
    # asking everyone to hand-edit the connection string they copied.
    for prefix in ("postgresql://", "postgres://"):
        if url.startswith(prefix):
            return "postgresql+psycopg://" + url[len(prefix) :]
    return url


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    return create_engine(_database_url(), pool_pre_ping=True)


@lru_cache(maxsize=1)
def _session_factory() -> sessionmaker[Session]:
    return sessionmaker(bind=get_engine())


def get_session() -> Session:
    return _session_factory()()
