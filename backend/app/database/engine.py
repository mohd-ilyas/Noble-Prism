"""
Database engine factory.
Automatically falls back to SQLite when PostgreSQL is unavailable.
"""
from __future__ import annotations

import logging

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

logger = logging.getLogger(__name__)


def _make_engine():
    url = settings.DATABASE_URL
    connect_args = {}

    if url.startswith("sqlite"):
        # SQLite needs check_same_thread disabled for FastAPI
        connect_args = {"check_same_thread": False}
        engine = create_engine(url, connect_args=connect_args, echo=False)

        # Enable WAL mode for better concurrency
        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(conn, _):
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA foreign_keys=ON")

        logger.info("Using SQLite fallback at %s", url)
        return engine

    # PostgreSQL path
    try:
        engine = create_engine(
            url,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20,
            echo=False,
        )
        # Quick connectivity test
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Connected to PostgreSQL")
        return engine
    except Exception as exc:
        logger.warning("PostgreSQL unavailable (%s) — falling back to SQLite", exc)
        fallback = "sqlite:///./nobleprism.db"
        fallback_engine = create_engine(
            fallback,
            connect_args={"check_same_thread": False},
            echo=False,
        )

        @event.listens_for(fallback_engine, "connect")
        def _sqlite_pragma(conn, _):
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA foreign_keys=ON")

        return fallback_engine


engine = _make_engine()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI dependency that yields a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
