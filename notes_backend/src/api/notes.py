from __future__ import annotations

from typing import List

from bson import ObjectId
from fastapi import APIRouter, HTTPException, Path, status
from pydantic import BaseModel, Field

from src.db.mongo import get_database
from src.models.note import NoteCreate, NoteOut, NoteUpdate, utcnow

router = APIRouter(prefix="/notes", tags=["Notes"])


class DeleteResponse(BaseModel):
    """Response returned after successful deletion."""

    deleted: bool = Field(..., description="Whether a note was deleted.")


def _parse_object_id(note_id: str) -> ObjectId:
    """Parse and validate a MongoDB ObjectId from a string."""
    try:
        return ObjectId(note_id)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid note id: {note_id}",
        ) from exc


def _note_doc_to_out(doc: dict) -> NoteOut:
    """Convert a MongoDB document into the API NoteOut model."""
    return NoteOut(
        id=str(doc["_id"]),
        title=doc.get("title", ""),
        content=doc.get("content", ""),
        created_at=doc["created_at"],
        updated_at=doc["updated_at"],
    )


@router.get(
    "",
    response_model=List[NoteOut],
    summary="List notes",
    description="Return all notes sorted by updated_at descending.",
    operation_id="list_notes",
)
async def list_notes() -> List[NoteOut]:
    """List all notes."""
    db = get_database()
    cursor = db.notes.find({}).sort("updated_at", -1)
    docs = await cursor.to_list(length=500)
    return [_note_doc_to_out(d) for d in docs]


@router.get(
    "/{id}",
    response_model=NoteOut,
    summary="Get note",
    description="Fetch a single note by its id (MongoDB ObjectId as string).",
    operation_id="get_note",
)
async def get_note(
    id: str = Path(..., description="Note id (MongoDB ObjectId as string)."),
) -> NoteOut:
    """Get a note by id."""
    db = get_database()
    oid = _parse_object_id(id)

    doc = await db.notes.find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return _note_doc_to_out(doc)


@router.post(
    "",
    response_model=NoteOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create note",
    description="Create a new note.",
    operation_id="create_note",
)
async def create_note(payload: NoteCreate) -> NoteOut:
    """Create a new note."""
    db = get_database()
    now = utcnow()

    doc = {
        "title": payload.title,
        "content": payload.content,
        "created_at": now,
        "updated_at": now,
    }
    res = await db.notes.insert_one(doc)
    created = await db.notes.find_one({"_id": res.inserted_id})
    # Should exist since it was just inserted
    return _note_doc_to_out(created)  # type: ignore[arg-type]


@router.put(
    "/{id}",
    response_model=NoteOut,
    summary="Update note",
    description="Update an existing note by id. Only provided fields are updated.",
    operation_id="update_note",
)
async def update_note(
    payload: NoteUpdate,
    id: str = Path(..., description="Note id (MongoDB ObjectId as string)."),
) -> NoteOut:
    """Update a note."""
    db = get_database()
    oid = _parse_object_id(id)

    update_doc = {k: v for k, v in payload.model_dump().items() if v is not None}
    if not update_doc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update",
        )

    update_doc["updated_at"] = utcnow()

    res = await db.notes.update_one({"_id": oid}, {"$set": update_doc})
    if res.matched_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")

    doc = await db.notes.find_one({"_id": oid})
    return _note_doc_to_out(doc)  # type: ignore[arg-type]


@router.delete(
    "/{id}",
    response_model=DeleteResponse,
    summary="Delete note",
    description="Delete a note by id.",
    operation_id="delete_note",
)
async def delete_note(
    id: str = Path(..., description="Note id (MongoDB ObjectId as string)."),
) -> DeleteResponse:
    """Delete a note."""
    db = get_database()
    oid = _parse_object_id(id)

    res = await db.notes.delete_one({"_id": oid})
    if res.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")

    return DeleteResponse(deleted=True)
