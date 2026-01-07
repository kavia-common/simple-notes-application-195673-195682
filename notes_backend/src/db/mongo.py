import os
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

_client: Optional[AsyncIOMotorClient] = None


def _get_mongodb_url() -> str:
    """
    Build MongoDB URL from environment variables or fall back to platform defaults.

    The paired `database` container provides a working reference in its `db_connection.txt`:
    `mongodb://appuser:dbuser123@localhost:5000/myapp?authSource=admin`

    Env vars (preferred):
    - MONGODB_URL: full MongoDB connection string
    - MONGODB_DB: database name
    """
    # Prefer explicit URL from env
    url = os.getenv("MONGODB_URL")
    if url:
        return url

    # Sensible defaults (match the database container defaults)
    return "mongodb://appuser:dbuser123@localhost:5000/myapp?authSource=admin"


def _get_mongodb_db_name() -> str:
    """Resolve MongoDB database name from env (MONGODB_DB) or from URL default."""
    return os.getenv("MONGODB_DB", "myapp")


# PUBLIC_INTERFACE
def get_database() -> AsyncIOMotorDatabase:
    """Get a cached AsyncIOMotorDatabase instance for the application."""
    global _client

    if _client is None:
        _client = AsyncIOMotorClient(_get_mongodb_url())

    return _client[_get_mongodb_db_name()]
