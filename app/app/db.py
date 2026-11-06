"""Database setup.

DATABASE_URL comes from an environment variable so the same code runs with:
  - PostgreSQL in Docker Compose (production-like)
  - SQLite in tests / CI (no database server needed)
"""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./tasks.db")

# SQLite needs this flag when used from FastAPI's worker threads
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False)


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI dependency: one DB session per request, always closed afterwards."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
