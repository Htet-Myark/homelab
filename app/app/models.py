"""Database table (SQLAlchemy) and API schemas (Pydantic)."""

from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    done: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )


# --- Schemas: what the API accepts and returns (validated automatically) ---


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    done: bool | None = None


class TaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    done: bool
    created_at: datetime
