import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.notes import router as notes_router

openapi_tags = [
    {
        "name": "Health",
        "description": "Service health and readiness endpoints.",
    },
    {
        "name": "Notes",
        "description": "CRUD operations for notes.",
    },
]


def _parse_cors_allow_origins() -> list[str]:
    """
    Resolve allowed CORS origins from environment.

    Priority:
    1) CORS_ALLOW_ORIGINS: comma-separated list of allowed origins
       Example: "http://localhost:3000,https://my-frontend.example.com"
    2) FRONTEND_URL: single frontend origin
       Example: "https://my-frontend.example.com"
    3) Default to local dev server.

    Note: In Kavia environments the frontend origin is typically NOT localhost,
    so this needs to be configurable to avoid browser CORS failures.
    """
    raw = (os.getenv("CORS_ALLOW_ORIGINS") or "").strip()
    if raw:
        return [o.strip().rstrip("/") for o in raw.split(",") if o.strip()]

    frontend_url = (os.getenv("FRONTEND_URL") or "").strip().rstrip("/")
    if frontend_url:
        return [frontend_url]

    return ["http://localhost:3000"]


app = FastAPI(
    title="Notes Backend API",
    description="FastAPI backend for a simple notes application using MongoDB.",
    version="0.1.0",
    openapi_tags=openapi_tags,
)

# Allow configured frontend origins (default to local dev server).
app.add_middleware(
    CORSMiddleware,
    allow_origins=_parse_cors_allow_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Health"], summary="Health check", operation_id="health_check")
def health_check():
    """Health check endpoint used for smoke tests and container orchestration."""
    return {"message": "Healthy"}


app.include_router(notes_router)
