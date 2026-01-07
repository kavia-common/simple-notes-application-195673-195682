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

app = FastAPI(
    title="Notes Backend API",
    description="FastAPI backend for a simple notes application using MongoDB.",
    version="0.1.0",
    openapi_tags=openapi_tags,
)

# Allow the React dev server.
# If you deploy the frontend elsewhere, add that origin (or set a proper env-driven allowlist).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Health"], summary="Health check", operation_id="health_check")
def health_check():
    """Health check endpoint used for smoke tests and container orchestration."""
    return {"message": "Healthy"}


app.include_router(notes_router)
