from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class NoteBase(BaseModel):
    """Shared fields for a note."""

    title: str = Field(..., min_length=1, max_length=200, description="Short note title.")
    content: str = Field(..., description="Note content (free-form text).")


class NoteCreate(NoteBase):
    """Payload for creating a note."""


class NoteUpdate(BaseModel):
    """Payload for updating a note (partial update semantics via PUT for simplicity)."""

    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Short note title.")
    content: Optional[str] = Field(None, description="Note content (free-form text).")


class NoteOut(NoteBase):
    """Note returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Note identifier (MongoDB ObjectId as string).")
    created_at: datetime = Field(..., description="UTC timestamp when the note was created.")
    updated_at: datetime = Field(..., description="UTC timestamp when the note was last updated.")


# PUBLIC_INTERFACE
def utcnow() -> datetime:
    """Return timezone-aware current UTC time."""
    return datetime.now(timezone.utc)
